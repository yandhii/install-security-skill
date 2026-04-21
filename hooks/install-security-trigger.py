#!/usr/bin/env python3
"""
PreToolUse/Bash hook: blocks install/update commands until /install-security
audit is completed and the user confirms. Checks the full session transcript
so the audit bypass works across multi-turn conversations (e.g. user gives
feedback, Claude makes changes, then retries the install).
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
    r'\bnpx\s+\S',
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

# Signals that the audit was completed somewhere in the session
AUDIT_SIGNALS = [
    r'/install-security',
    r'install.security',
    r'security audit',
    r'安全审计',
    r'audit.*complet',
    r'Security Audit:',      # report header
    r'Recommendation:.*[Ii]nstall',
]
AUDIT_RE = [re.compile(p, re.IGNORECASE) for p in AUDIT_SIGNALS]

# User confirmation signals (must appear AFTER an audit signal)
CONFIRM_SIGNALS = [
    r'\byes\b', r'\b是\b', r'\b确认\b', r'\bproceed\b', r'\bconfirm\b',
    r'\b继续\b', r'\bokay\b', r'\bok\b',
]
CONFIRM_RE = [re.compile(p, re.IGNORECASE) for p in CONFIRM_SIGNALS]

# How many recent transcript messages to scan (keep bounded)
TRANSCRIPT_LOOKBACK = 30


def is_install_command(cmd: str) -> bool:
    return any(p.search(cmd) for p in COMPILED)


def audit_confirmed_in_transcript(transcript_path: str) -> bool:
    """
    Reads the session transcript and checks whether:
    1. An audit signal appears in any assistant message, AND
    2. A user confirmation appears in a human message AFTER that audit signal.
    """
    try:
        with open(transcript_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return False

    recent = lines[-TRANSCRIPT_LOOKBACK:]
    audit_seen = False

    for line in recent:
        try:
            entry = json.loads(line)
        except Exception:
            continue

        role = entry.get("role", "")
        # Extract text content regardless of content structure
        content = entry.get("content", "")
        if isinstance(content, list):
            text = " ".join(
                c.get("text", "") for c in content if isinstance(c, dict)
            )
        else:
            text = str(content)

        if role == "assistant" and not audit_seen:
            if any(p.search(text) for p in AUDIT_RE):
                audit_seen = True

        elif role == "user" and audit_seen:
            if any(p.search(text) for p in CONFIRM_RE):
                return True

    return False


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

    # Check current assistant message first (fast path)
    assistant_msg = data.get("assistant_message", "") or ""
    if any(p.search(assistant_msg) for p in AUDIT_RE):
        return

    # Check full transcript for audit + confirmation across multiple turns
    transcript_path = data.get("transcript_path", "")
    if transcript_path and audit_confirmed_in_transcript(transcript_path):
        return

    print(json.dumps({
        "decision": "block",
        "reason": (
            "BLOCKED. Do the following right now in this response, without asking the user:\n"
            "1. Invoke the /install-security skill for the package in the blocked command.\n"
            "2. Run the full audit and display the complete report.\n"
            "3. End with exactly: 'Do you want to proceed with the install/update? (yes / no)'\n"
            "Do not retry the blocked command until the user replies 'yes'."
        )
    }))


if __name__ == "__main__":
    main()
