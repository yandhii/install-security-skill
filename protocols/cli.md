# CLI Tool Audit Protocol

## Stop Early

Stop immediately and output a verdict if you find:

- Install method is piped shell execution (`curl | bash`, `wget | sh`) with no checksum verification option
- Confirmed malicious advisory for this tool
- Binary is self-updating from a remote URL without user confirmation

## Critical Path

1. Install method (piped shell vs package manager vs binary + checksum)
2. Binary provenance (CI-built? checksums published?)
3. Repo health

1. **Find the repo**
   - Tool: `WebSearch` → `<name> cli github`

2. **Repo health**
   - Tool: `Bash` → `gh repo view <owner/repo> --json stargazerCount,updatedAt,licenseInfo,description`
   - Apply combined weak-signal assessment from severity.md

3. **If npm-based: Socket scan**
   - Tool: `Bash` → `npx @socketsecurity/cli npm install <pkg> --dry-run`

4. **Install method**
   - Tool: `WebFetch` → README
   - Flag 🔴 for piped shell execution without checksums
   - Flag 🟢 for package manager installs
   - Flag 🟡 for manual binary download without checksums

5. **Binary provenance**
   - Are releases built via CI (GitHub Actions)?
   - Are checksums/signatures published?
   - Flag 🟡 if neither

6. **Homebrew tap (if applicable)**
   - Official `homebrew/core` formulae: lower risk
   - Custom taps (`brew tap user/repo`): 🟡 by default — review tap repo health and formula source
   - Check whether bottles and checksums are published
   - Flag 🔴 if formula install logic relies on piped remote shell

→ Output: @shared/verdict.md
