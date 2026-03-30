# PyPI Audit Protocol

1. **Metadata**
   - Tool: `Bash` → `curl -s https://pypi.org/pypi/<pkg>/json | jq '{name,version:.info.version,author:.info.author,license:.info.license,project_urls:.info.project_urls,requires_dist:.info.requires_dist}'`

2. **Source trust**
   - Check if `project_urls` (homepage, source, docs) all point to the same project
   - Flag 🟡 if inconsistent or missing
   - Apply source-trust.md signals

3. **Distribution type**
   - Tool: `Bash` → `curl -s https://pypi.org/pypi/<pkg>/json | jq '.urls[].packagetype'`
   - Flag 🟡 if only pre-built wheels exist with no source distribution — harder to review

4. **Entry points / CLI commands**
   - Tool: `Bash` → `curl -s https://pypi.org/pypi/<pkg>/json | jq '.info.requires_dist'`
   - Note any CLI commands installed

5. **Release timeline**
   - Tool: `Bash` → `curl -s https://pypi.org/pypi/<pkg>/json | jq '.releases | keys'`
   - Flag 🟡 if brand new package, sudden major version jump, or many releases in short period from unknown author

6. **`.pth` file check**
   - Tool: `Bash` → `curl -s https://pypi.org/pypi/<pkg>/json | jq '.urls[].filename'`
   - If wheel is available, check its contents: `pip download <pkg> --no-deps -d /tmp/pkgcheck && unzip -l /tmp/pkgcheck/*.whl | grep '\.pth'`
   - Flag 🔴 if `.pth` files contain executable import statements beyond path configuration
   - Flag 🟡 if `.pth` files are present at all — note the inherent startup execution risk

7. **Typosquat check**
   - Apply heuristics from typosquat.md (e.g., `request` vs `requests`, `python-dotenv` vs `dotenv`)

8. **Build/install behavior**
   - Flag 🟡 if source distribution requires executing `setup.py` or custom build backend
   - Escalate to 🔴 if it downloads remote content or executes shell commands unrelated to building
