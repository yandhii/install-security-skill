# npm Audit Protocol

## Stop Early

Stop the audit immediately and output a verdict if you find any of the following — do not continue to remaining steps:

- `preinstall` / `postinstall` / `install` script that downloads and executes remote content (confirmed curl/wget/fetch + exec pattern)
- Package confirmed malicious in the GitHub Advisory Database, npm audit, or OSV
- High-confidence typosquat of a security-critical package (crypto, auth, payments, signing)
- Any ⛔ REJECT pattern from @patterns/supply-chain.md or @patterns/prompt-injection.md

## Critical Path

If time-constrained, run these three first — they decide most verdicts:
1. Publish age (7-day rule)
2. Install scripts (`preinstall`, `postinstall`)
3. Typosquat check

1. **Metadata + Publish Age** ⚠️ Hard rule
   - Tool: `Bash` → `curl -s https://registry.npmjs.org/<pkg> | jq '{name,description,license,maintainers,time}'`
   - Extract: name, latest version, license, maintainers, creation date, last publish date
   - **BLOCK if the target version was published < 7 days ago.** Use the previous stable version instead and tell the user why.
   - Check publish time: `npm view <pkg>@<version> time --json` or inspect the `time` map from the registry response

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

9. **Version delta check** (catches version-poisoning attacks like axios 1.14.1)
   - Compare deps of target version vs. previous stable:
     ```bash
     npm view <pkg>@<prev> dependencies --json
     npm view <pkg>@<target> dependencies --json
     ```
   - Flag 🔴 if a new dependency appears that meets **2 or more** of: < 1000 weekly downloads, published within days of this version, no source repo — any single signal alone is 🟡
   - Check new dep's own install scripts: `npm view <new-dep> scripts --json`
   - Check new dep publish date: `npm view <new-dep> time --json | jq 'to_entries | sort_by(.value) | last'`

10. **Socket scan**
    - Tool: `Bash` → `npx @socketsecurity/cli npm install <pkg> --dry-run`

## Post-Verdict Output Requirements

After giving a verdict, always output the install command in this form:

```json
// package.json — exact version, no ^ or ~
"dependencies": {
  "<pkg>": "<exact-version>"
}
```

Then remind the user to:
1. Commit `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` — **never `.gitignore` lockfiles**
2. Use `npm ci` in CI/CD instead of `npm install`
