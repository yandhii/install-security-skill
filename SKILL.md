---
name: install-security
description: Automatic security audit before installing any package, tool, or integration. Triggers when the user clearly intends to install, add, or integrate a third-party package, dependency, CLI tool, MCP server, or Claude skill. Strong triggers include install commands (npm install, pip install, cargo install, brew install, npx), raw script execution (curl | bash, wget | sh, any URL piped to a shell), explicit install intent (安装, 装一下, 加依赖, 加个包, 装个插件, 装个 MCP, 装个 skill, 我想安装, 帮我装), or references to adding an MCP server to config. A URL containing an install script (e.g. install.sh, get.sh) paired with any install intent is always a strong trigger. Weak triggers like 配置, 试试, 用一下 require context — only trigger if a specific third-party artifact is named. Do NOT trigger for generic configuration, code editing, or feature requests. Run the full audit and present findings BEFORE asking the user to confirm. Do not wait to be asked for a security review — it is the default behavior.
---

# Install Security Protocol

Run the appropriate audit and present a verdict BEFORE proceeding with any installation.
Never install first and audit later. Never output an install command until the user confirms.

## 0. Pre-Execution

### Input Sanitization

Before interpolating any name into shell commands, validate format by type:

- **npm**: `^(?:@[a-zA-Z0-9._-]+\/)?[a-zA-Z0-9._-]+$`
- **PyPI**: `^[a-zA-Z0-9._-]+$`
- **Cargo crate**: `^[a-zA-Z0-9_-]+$`
- **GitHub repo**: `^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$`

Reject anything containing `;`, `&`, `|`, `$`, backticks, or other shell metacharacters.
If validation fails, ask the user to provide the exact name — do not guess or construct commands.

### Environment Fallback

If terminal tools (`curl`, `jq`, `gh`) are unavailable, use WebSearch and WebFetch to query registries and GitHub directly. Do NOT fabricate command outputs.

## Dispatch

Determine artifact type, then follow the corresponding protocol:

| Type | Protocol |
|------|----------|
| npm package | @protocols/npm.md |
| PyPI package | @protocols/pypi.md |
| Cargo crate | @protocols/cargo.md |
| MCP server | @protocols/mcp.md |
| CLI tool | @protocols/cli.md |
| Claude skill | @protocols/skill.md |
| URL or document | @reviews/url-document.md |

Shared references used by all protocols:
- Severity system: @shared/severity.md
- Source trust signals: @shared/source-trust.md
- Typosquat detection: @shared/typosquat.md
- Verdict format: @shared/verdict.md

Pattern libraries (referenced by protocols):
- Code red flags: @patterns/code-red-flags.md
- Supply chain attacks: @patterns/supply-chain.md
- Prompt injection: @patterns/prompt-injection.md

## Fast Path

For well-known packages (`typescript`, `react`, `lodash`, `requests`, `tokio`, etc.) with verified publishers and very high download counts, perform a reduced audit — not no audit:

1. Confirm exact package name and registry source
2. Confirm publisher/owner matches expected
3. Check latest version number and publish date
4. Check install scripts
5. Lightweight typosquat validation
6. Proceed if clean

Fast path = light audit, never skip audit.

## Non-Registry Sources

- **Git URL**: Default 🟡 — no registry vetting. Check repo health via mcp.md/cli.md steps.
- **Raw script URL**: Default 🔴 unless checksums are verified.
- **Tarball / local path**: Note that upstream provenance cannot be verified. Mark audit confidence as Low.
- **Private registry**: Do not assume safe merely because private. Note metadata cannot be independently verified.
