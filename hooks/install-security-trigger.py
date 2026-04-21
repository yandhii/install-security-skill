#!/usr/bin/env python3
"""
PreToolUse/Bash hook: intercepts install commands and injects a
system message telling Claude to invoke the install-security skill
before proceeding.
"""
import sys
import json
import re

# Patterns that indicate an install or update action
INSTALL_PATTERNS = [
    # installs
    r'\bnpm\s+install\b',
    r'\bnpm\s+i\b',
    r'\bpnpm\s+(add|install)\b',
    r'\byarn\s+add\b',
    r'\bpip\s+install\b',
    r'\buv\s+add\b',
    r'\buv\s+pip\s+install\b',
    r'\bcargo\s+add\b',
    r'\bcargo\s+install\b',
    r'\bbrew\s+install\b',
    r'\bapt(-get)?\s+install\b',
    r'\bapk\s+add\b',
    r'\bclaude\s+(plugin\s+)?(skills?\s+)?(add|install)\b',
    r'curl\s+.+\|\s*(ba)?sh',
    r'wget\s+.+\|\s*(ba)?sh',
    r'\bnpx\s+\S',             # npx <pkg> often installs implicitly
    # updates — same supply-chain risk as fresh installs
    r'\bnpm\s+(update|upgrade)\b',
    r'\bpnpm\s+(update|upgrade)\b',
    r'\byarn\s+upgrade\b',
    r'\bpip\s+install\s+.*--upgrade\b',
    r'\bpip\s+install\s+-[A-Za-z]*U\b',
    r'\buv\s+pip\s+install\s+.*--upgrade\b',
    r'\bcargo\s+update\b',
    r'\bbrew\s+upgrade\b',
    r'\bapt(-get)?\s+upgrade\b',
    r'\bclaude\s+plugin\s+update\b',
    r'\bclaude\s+update\b',
]

COMPILED = [re.compile(p, re.IGNORECASE) for p in INSTALL_PATTERNS]

# Keywords that signal the audit already happened in this turn
AUDIT_SIGNALS = [
    r'/install-security',
    r'install.security',
    r'security audit',
    r'安全审计',
    r'audit.*complet',
]
AUDIT_RE = [re.compile(p, re.IGNORECASE) for p in AUDIT_SIGNALS]


def is_install_command(cmd: str) -> bool:
    return any(p.search(cmd) for p in COMPILED)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    if data.get("tool_name") != "Bash":
        return

    cmd = data.get("tool_input", {}).get("command", "")
    if not is_install_command(cmd):
        return

    # If the model output in this turn already mentioned the skill, skip
    assistant_msg = data.get("assistant_message", "") or ""
    if any(p.search(assistant_msg) for p in AUDIT_RE):
        return

    print(json.dumps({
        "systemMessage": (
            "⚠️  INSTALL DETECTED — invoke the /install-security skill "
            "and complete the full audit BEFORE running this command. "
            "Do not execute the install until the audit verdict is presented to the user."
        )
    }))


if __name__ == "__main__":
    main()
