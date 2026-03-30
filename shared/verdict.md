# Verdict Format

## Report Template

```
## Security Audit: <name>

**Key facts**
- Ecosystem: [npm / PyPI / crates.io / MCP / CLI / Skill / URL]
- Package: <exact name>
- Version: <version reviewed>
- Source: <registry URL or repo URL>
- Publisher: <name or org>
- Audit confidence: [High / Medium / Low]

⛔ REJECT (n findings)
- [confirmed malicious — no user override]

🔴 RED (n findings)
- [finding]

🟡 YELLOW (n findings)
- [finding]

🟢 GREEN
- [finding]

**Context reminder**: [Note if installing with elevated privileges, in CI with secrets, or granting agent autonomy — these increase effective risk of any yellow/red finding]

**Recommendation**: [Install / Install with caution / Do not install / Do not install — confirmed malicious]
```

## Audit Confidence

- **High**: All checks completed, metadata verified, source code reviewed
- **Medium**: Some checks could not be completed (e.g., API rate-limited, source not fully readable)
- **Low**: Critical metadata missing, source unavailable, or non-registry install with no verification

If confidence is Low, default recommendation should be "Install with caution" at best.

## After User Confirms

Only after the user explicitly confirms, provide an install command with **exact version pinning to the version reviewed**. This prevents attacks where the registry updates the package between the audit and the install:

- npm: `npm install <pkg>@<exact-version>`
- pip: `pip install <pkg>==<exact-version>` (suggest virtual environment)
- cargo: `cargo install <pkg> --version <exact-version>`
- For binary installs: include checksum verification step if available
- For non-registry sources: pin exact artifact identity — commit SHA for Git URLs, release checksum for binaries

If the user requests a different version than what was audited, re-run the audit for that version.

## Post-Install Verification

After providing the install command and the user confirms, append:

```bash
# Verify the installed artifact with Snyk Agent Scan:
uvx snyk-agent-scan==0.4.10 --skills ~/.claude/skills/<skill-name>
# Or for MCP servers, scan the relevant config:
uvx snyk-agent-scan==0.4.10 ~/.claude/claude_desktop_config.json
```

- Requires a free Snyk account and `export SNYK_TOKEN=<your-token>`
- Uploads skill/MCP content to Snyk's API for server-side analysis — skip if the artifact is private/sensitive
- This is a complementary post-install check, not a substitute for the pre-install audit above

## Minimal Privilege Suggestions

When providing the install command, also suggest:

- Avoid `sudo` / admin installs unless necessary
- Use isolated environments: `venv` for Python, project-local `node_modules` for npm
- Consider `npm install --ignore-scripts` for initial inspection
- For MCP servers: start with minimal permissions, restrict directory scope where possible

## Separation of Audit and Execution

- Never output an install command inside the audit report
- If any ⛔ REJECT findings exist, do not provide an install command. Period. No override.
- If any 🔴 RED findings exist, do not provide an install command unless the user explicitly overrides
- The audit report is information; the install command is a separate action gated on user confirmation

## General Notes

- **Best-effort disclaimer**: This audit is a best-effort supply-chain review, not a guarantee of safety. Always note this if the user treats "no findings" as "proven safe."
- If a network request fails, note the failure explicitly and reduce audit confidence. Do not silently skip checks.
- If the user says "just install it" or "skip the audit", remind them once of the risks, then comply.
- Context risk escalation: if installing with root/admin privileges or granting autonomous agent access, note this and consider escalating severity of yellow findings.
