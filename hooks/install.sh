#!/usr/bin/env bash
# install-security hook installer
# Copies install-security-trigger.py into ~/.claude/hooks/ and registers
# a PreToolUse/Bash hook in ~/.claude/settings.json.
set -e

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS="$CLAUDE_DIR/settings.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_FILE="install-security-trigger.py"

# Require python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required." && exit 1
fi

mkdir -p "$HOOKS_DIR"
cp "$SCRIPT_DIR/$HOOK_FILE" "$HOOKS_DIR/$HOOK_FILE"
chmod +x "$HOOKS_DIR/$HOOK_FILE"
echo "  Installed: $HOOKS_DIR/$HOOK_FILE"

# Patch settings.json (idempotent)
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
cp "$SETTINGS" "$SETTINGS.bak"

python3 - "$SETTINGS" "$HOOKS_DIR/$HOOK_FILE" <<'EOF'
import sys, json
settings_path, hook_path = sys.argv[1], sys.argv[2]
with open(settings_path) as f:
    s = json.load(f)
s.setdefault("hooks", {}).setdefault("PreToolUse", [])
already = any(
    any(h.get("command", "").endswith("install-security-trigger.py")
        for h in e.get("hooks", []))
    for e in s["hooks"]["PreToolUse"]
)
if not already:
    s["hooks"]["PreToolUse"].append({
        "matcher": "Bash",
        "hooks": [{
            "type": "command",
            "command": f'python3 "{hook_path}"',
            "timeout": 5,
            "statusMessage": "Checking install security..."
        }]
    })
    with open(settings_path, "w") as f:
        json.dump(s, f, indent=2)
        f.write("\n")
    print("  Hook registered in settings.json")
else:
    print("  Hook already registered, skipping.")
EOF

echo ""
echo "Done. Restart Claude Code to activate."
echo "The hook will intercept install/update commands and invoke /install-security before proceeding."
