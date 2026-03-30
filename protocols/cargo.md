# Cargo (crates.io) Audit Protocol

1. **Metadata**
   - Tool: `Bash` → `curl -s https://crates.io/api/v1/crates/<pkg> | jq '{name:.crate.name,version:.crate.max_stable_version,downloads:.crate.downloads,updated_at:.crate.updated_at,repository:.crate.repository,homepage:.crate.homepage}'`

2. **Downloads**
   - Low all-time downloads (< 5,000) are a weak signal — meaningful only when combined with other concerns

3. **Source trust**
   - Check repository/homepage consistency
   - Apply source-trust.md signals

4. **`build.rs` check**
   - Tool: `Bash` → `gh api repos/<owner/repo>/contents/build.rs 2>/dev/null | jq -r '.content' | base64 -d 2>/dev/null | head -50`
   - Flag 🟡 if present (executes at compile time)
   - Escalate to 🔴 if `build.rs` contains network requests, downloads, or shell execution

5. **Build-dependencies & proc-macros**
   - Tool: `Bash` → `gh api repos/<owner/repo>/contents/Cargo.toml | jq -r '.content' | base64 -d | grep -A 20 'build-dependencies\|proc-macro'`
   - Flag 🟡 for awareness — both execute code during build/compile time

6. **Maintenance**
   - Tool: `Bash` → `gh repo view <owner/repo> --json stargazerCount,updatedAt,openIssues`
   - Check last update, open issues, CI status

7. **Typosquat check**
   - Apply heuristics from typosquat.md
