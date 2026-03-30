# MCP Server Audit Protocol

## 1. Find the repo
- Tool: `WebSearch` → `<name> MCP server github`
- Get the GitHub owner/repo slug

## 2. Repo health
- Tool: `Bash` → `gh repo view <owner/repo> --json stargazerCount,updatedAt,licenseInfo,openIssues,description`
- Apply combined weak-signal assessment from severity.md — don't flag on a single metric alone

## 3. Capability review (most important)

Identify the server's effective permissions:

| Capability | What to look for | Risk level |
|---|---|---|
| Shell execution | `child_process`, `exec`, `spawn` | 🟡 if expected for purpose; 🔴 if obfuscated or running remote content |
| Filesystem | `fs.*` calls, path scope | 🟡 if scoped to project dir; 🔴 if accessing home/root/arbitrary paths |
| Network | `fetch`, `axios`, `http.*` | 🟡 if calling expected API; 🔴 if calling unrelated domains |
| Browser automation | Puppeteer, Playwright, Selenium | 🟡 inherently — can access arbitrary web content |
| Credentials/env | `process.env`, dotenv, keychain | 🟡 for documented config; 🔴 if reading undocumented secrets |
| Database | DB drivers, SQL execution | 🟡 if read-only; 🔴 if write access to production data |

**High-risk combinations**: shell + network + broad filesystem (especially with credential access) = 🔴 unless tightly scoped and clearly justified.

## 4. Source code scan
- Tool: `Bash` → `gh api repos/<owner/repo>/contents/` to find entry points
- Tool: `WebFetch` → raw source files (index.ts / index.js / src/index.*)
- Assess whether capabilities match stated purpose — a git MCP using `spawn('git', ...)` is fine; a "weather" MCP using `exec(userInput)` is not

## 5. Install scripts
- Tool: `Bash` → `gh api repos/<owner/repo>/contents/package.json | jq -r '.content' | base64 -d | jq '.scripts'`
- Flag 🔴 if requesting unrestricted Bash access

## 6. Permissions requested
- Tool: `WebFetch` → README
- Flag 🔴 if requesting unrestricted Bash or broad filesystem access without justification
