# npm Audit Protocol

1. **Metadata**
   - Tool: `Bash` → `curl -s https://registry.npmjs.org/<pkg> | jq '{name,description,license,maintainers,time}'`
   - Extract: name, latest version, license, maintainers, creation date, last publish date

2. **Downloads**
   - Tool: `Bash` → `curl -s https://api.npmjs.org/downloads/point/last-week/<pkg>`
   - Low download counts (< 500/week) are a weak signal — only meaningful combined with other concerns

3. **Source trust**
   - Check §source-trust.md signals
   - Flag 🟡 if `repository` field is missing or inconsistent with publisher

4. **Install scripts**
   - Tool: `Bash` → `npm view <pkg> scripts --json`
   - Check `preinstall`, `postinstall`, `prepare`, `prepublish`
   - Flag 🔴 if they contain remote fetch + execute patterns
   - Flag 🟡 if they invoke local build scripts or use `node -e` without obvious remote fetch

5. **`bin` field**
   - Tool: `Bash` → `npm view <pkg> bin --json`
   - Note what CLI commands are installed globally — these execute with user privileges

6. **Dependencies**
   - Tool: `Bash` → `npm view <pkg> dependencies --json`
   - High direct dependency count (> 20) is a weak signal — only elevate if combined with poor source trust

7. **Typosquat check**
   - Apply heuristics from typosquat.md

8. **Maintainer check**
   - Tool: `Bash` → `gh user view <maintainer>`
   - Flag 🟡 if new/low-history account combined with typosquat-like naming or rapid package creation

9. **Socket scan**
   - Tool: `Bash` → `npx @socketsecurity/cli npm install <pkg> --dry-run`
