# Verdict Format

## Summary Mode

For Fast Path audits with no RED/YELLOW findings, use this condensed format instead of the full report:

```
**[Package name]** — ✅ PASS
- Ecosystem: [type] | Publisher: [name] | Version: [x.y.z] | Published: [N days ago]
- [One-line summary, e.g. "Well-known package, verified publisher, no install hooks"]
- Confidence: High
- Recommendation: Install
```

Use Summary Mode only when **all** of:
- Fast Path applies (well-known package, verified publisher, high downloads)
- **All applicable protocol checks have been completed** — do not use mid-audit on the basis that nothing has been found so far
- All findings are 🟢 GREEN or none
- Confidence is explicitly High (not assumed)

Use the full report template for any 🟡 YELLOW, 🔴 RED, or ⛔ REJECT finding, or when confidence is Medium/Low.

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

### Confidence Downgrade Triggers

Downgrade automatically — do not stay at the default level when evidence is incomplete:

**High → Medium** if any of:
- Registry API returned incomplete or malformed data
- Version publish date could not be retrieved
- Install scripts could not be fetched or parsed
- Source repository is unavailable, private, or returns errors

**Medium → Low** if any of:
- Package source code is unavailable for review
- Artifact is from a non-registry source (Git URL, tarball, raw script URL)
- Critical metadata (publisher identity, version, license) is missing or contradictory
- Network errors blocked more than one key check from completing

**Rule**: Never report "no issues found" when confidence is Low. Always name the gaps explicitly in the verdict — which checks were skipped and why.

## After User Confirms

Only after the user explicitly confirms, provide an install command with **exact version pinning to the version reviewed**. This prevents attacks where the registry updates the package between the audit and the install:

- npm: `npm install <pkg>@<exact-version>`
- pip: `pip install <pkg>==<exact-version>` (suggest virtual environment)
- cargo: `cargo install <pkg> --version <exact-version>`
- For binary installs: include checksum verification step if available
- For non-registry sources: pin exact artifact identity — commit SHA for Git URLs, release checksum for binaries

If the user requests a different version than what was audited, re-run the audit for that version.

## Safer Install Alternatives

When a 🟡 YELLOW finding involves **remote download without checksum** (e.g. `curl -fsSL ... | bash`, install script that fetches files from a raw URL at install time, `claude plugin add` pulling from a live GitHub branch), proactively offer a safer local-clone path **before** providing the standard install command. Do not wait for the user to ask.

### When to offer

Offer if **any** of these apply:
- Install script downloads files from a remote URL during execution (no SHA/checksum verification)
- The install command targets a branch tip (e.g. `main`) rather than a tagged release or commit SHA
- The artifact is a non-registry GitHub source and the plugin system does not support version pinning

### What to offer

```bash
# 1. Clone and pin to the exact commit SHA that was audited
git clone https://github.com/<owner>/<repo>.git
cd <repo>
git checkout <commit-sha>   # SHA of the reviewed tag/release

# 2. Install from local path — no further remote fetching
<ecosystem-specific local install command>
# e.g. claude plugin add .        (Claude Code skills)
#      npm install .               (npm packages)
#      pip install .               (Python packages)
#      cargo install --path .      (Rust crates)
```

**Why this is safer**: the bytes installed are identical to what was audited. A subsequent compromise of the upstream repo or CDN cannot affect this install. The risk window closes at `git checkout`.

### When not to offer

- Registry installs with exact version pinning (`npm install pkg@1.2.3`, `pip install pkg==1.2.3`) — the registry already pins the artifact by content hash
- Install scripts that verify checksums themselves before executing downloaded content
- The user has already opted into the standard path after being informed of the risk

Always note the trade-off: local clone requires manual re-clone + re-audit for future updates, whereas the plugin system handles updates automatically (with the associated supply-chain risk).

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
- If the highest finding is 🟡 YELLOW, present findings and wait for explicit user confirmation before providing the install command
- The audit report is information; the install command is a separate action gated on user confirmation at every severity level

## General Notes

- **Best-effort disclaimer**: This audit is a best-effort supply-chain review, not a guarantee of safety. Always note this if the user treats "no findings" as "proven safe."
- If a network request fails, note the failure explicitly and reduce audit confidence. Do not silently skip checks.
- If the user says "just install it" or "skip the audit", remind them once of the risks, then comply.
- Context risk escalation: if installing with root/admin privileges or granting autonomous agent access, note this and consider escalating severity of yellow findings.
