# install-security

A Claude Code skill that automatically audits any package, tool, or integration before installation — triggered by install intent in English or Chinese.

## What it does

Runs a supply-chain security audit and presents a verdict **before** any install command is executed. Never installs first and audits later.

## Triggers

**Strong** — always audits:
- Install commands: `npm install`, `pip install`, `cargo install`, `brew install`, `npx`, `curl | bash`
- Explicit install intent: 安装, 装一下, 加依赖, 加个包, 装个插件, 装个 MCP, 装个 skill

**Weak** — audits only if a specific third-party artifact is named:
- 配置, 试试, 用一下

Does **not** trigger for generic configuration, code editing, or feature requests.

## Supported artifact types

| Type | Protocol |
|------|----------|
| npm package | `protocols/npm.md` |
| PyPI package | `protocols/pypi.md` |
| Cargo crate | `protocols/cargo.md` |
| MCP server | `protocols/mcp.md` |
| CLI tool | `protocols/cli.md` |
| Claude skill | `protocols/skill.md` |
| URL / raw script | `reviews/url-document.md` |

## Structure

```
install-security/
├── SKILL.md                  # Skill entry point and dispatch logic
├── protocols/                # Per-ecosystem audit protocols
├── reviews/                  # URL and document review
├── shared/                   # Severity system, verdict format, source trust, typosquat detection
└── patterns/                 # Code red flags, supply chain attacks, prompt injection patterns
```

## Severity levels

- **⛔ REJECT** — Confirmed malicious. No user override. No install command provided.
- **🔴 RED** — High-risk. Block by default; user must explicitly override.
- **🟡 YELLOW** — Flag clearly; proceed if user confirms.
- **🟢 GREEN** — Informational clean signals.
