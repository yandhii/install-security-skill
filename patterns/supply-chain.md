# Supply Chain Attack Patterns

Reference library for identifying supply chain attacks across all ecosystems.

## 1. Pipe-to-Shell Execution

**Severity**: 🔴 RED unless checksums are verified
**Examples**: `curl https://example.com/install.sh | bash`, `wget -qO- url | sh`, `iwr url | iex` (PowerShell)
**Risk**: The remote script can change at any time between audit and execution. No integrity verification.
**Mitigation**: Download first, verify checksum, then execute.

## 2. Runtime Secondary Download

**Severity**: 🔴 RED
**Examples**:
- Python: `subprocess.run(["pip", "install", "undeclared-pkg"])`
- Node: `child_process.exec("npm install extra-pkg")`
- Shell: `curl $REMOTE_URL | bash` called from application code
**Risk**: Installs additional packages at runtime that were not reviewed at install time. Bypasses audit entirely.

## 3. One-Shot Execution Without Pinning

**Severity**: 🟡 YELLOW
**Examples**: `npx some-tool@latest`, `pipx run some-tool`
**Risk**: `@latest` resolves at execution time — a compromised new version runs immediately without re-audit.
**Mitigation**: Pin to exact version: `npx some-tool@1.2.3`.

## 4. Auto-Update Channels

**Severity**: 🔴 RED
**Examples**: Background updater polling `https://cdn.example.com/VERSION`, file-replacement logic triggered on startup
**Risk**: Creates a persistent remote code execution channel. If the update server or CDN is compromised, all installed copies are compromised silently.

## 5. Dependency Hijacking

**Severity**: 🔴 RED (high-confidence); 🟡 YELLOW (suspected)

| Variant | Description | Signal |
|---|---|---|
| Typosquatting | Name differs from popular package by 1 char | `axois`, `requets`, `lodahs` |
| Scope confusion | Mimics official scope from unrelated publisher | `@openai-tools/sdk` published by unknown |
| Prefix/suffix injection | Adds common affix to popular name | `node-lodash`, `py-requests`, `react-core-utils` |
| Abandoned package takeover | Original package unmaintained; new publisher claims it | Check publish date gap vs maintainer change |
| Star jacking | Fork inherits parent repo's star count | High stars, mismatched org, low download count |

See @shared/typosquat.md for detection heuristics.

## 6. Build-Time Injection

**Severity**: 🔴 RED if fetches remote content; 🟡 YELLOW if local-only

| Ecosystem | Entry point | What to check |
|---|---|---|
| npm | `postinstall`, `preinstall`, `install` in `package.json#scripts` | Does it run remote fetch or eval? |
| PyPI | `setup.py`, `setup.cfg`, `pyproject.toml` `[tool.setuptools]` | Does `setup.py` execute shell commands? |
| Cargo | `build.rs` | Does it make network calls or write outside `OUT_DIR`? |
| General | `Makefile`, `CMakeLists.txt`, `configure` | Any `curl`, `wget`, or remote script references? |

**Detection**: `gh api repos/<owner/repo>/contents/package.json | jq -r '.content' | base64 -d | jq '.scripts'`

## 7. Trusted Source Compromise

**Severity**: ⛔ REJECT if confirmed via CVE/advisory; 🔴 RED if suspected
**Variants**:
- **Repo hijacking**: Original maintainer's GitHub account compromised; malicious commit pushed
- **Registry account takeover**: PyPI/npm account credentials stolen; malicious version published
- **CI/CD poisoning**: Build pipeline injected; distributed binary differs from source
- **CDN compromise**: Static asset host serving modified files

**Detection signals**: Sudden version published by different maintainer, unusual publish timestamp (off-hours), binary hash mismatch vs CI-published checksums, security advisories (GitHub Advisory DB, OSV, Snyk).
