# Code Red Flag Patterns

Reference library used by all audit protocols. When any of these patterns are detected, apply the severity rating shown.

## 1. Outbound Data Unauthorized Transmission

**Severity**: ⛔ REJECT if confirmed credential/secret transmission; 🔴 RED if suspected
**Keywords**: `curl`, `fetch`, `axios`, `http.post`, `requests.post`, `net/http`
**Trigger**: Any network call during install/startup that sends environment data, file contents, or identifiers to an external domain unrelated to the package's stated purpose.
**False positive guidance**: Telemetry with disclosed opt-in is 🟡. Calling the package's own documented API is expected.

## 2. Credential and Environment Variable Access

**Severity**: 🔴 RED if combined with network calls; 🟡 YELLOW if isolated config reads
**Keywords**: `process.env`, `os.environ`, `dotenv`, `keychain`, `~/.netrc`, `~/.npmrc`, `~/.pypirc`
**Trigger**: Reading undocumented env vars or secrets files, especially when paired with any outbound network call.

## 3. Filesystem Access Beyond Stated Scope

**Severity**: 🔴 RED if accessing home/root/arbitrary paths; 🟡 YELLOW if scoped to project dir
**Keywords**: `fs.readFileSync`, `open(`, `os.path`, `glob`, `Path(`
**Trigger**: Reading files outside the package's own directory without clear justification. Especially: reading all `.env` files, SSH keys, credential stores.

## 4. Agent-Sensitive Path Access

**Severity**: ⛔ REJECT — no legitimate reason for a third-party package to access these
**Paths to flag**: `~/.claude/`, `MEMORY.md`, `USER.md`, `IDENTITY.md`, `SOUL.md`, `paired.json`, `sessions.json`, `~/.ssh/`, `~/.aws/`, `~/.gnupg/`, `~/.config/`, `~/.npmrc`
**Trigger**: Any reference to these paths in install scripts, runtime code, or skill files.

## 5. Dynamic Code Execution

**Severity**: 🔴 RED if input is remote/user-controlled; 🟡 YELLOW if local and reviewable
**Keywords**: `eval(`, `exec(`, `Function(`, `compile(`, `importlib`, `__import__`
**Trigger**: Executing strings as code, especially strings fetched from the network or passed from user input. Obfuscated eval is always 🔴.

## 6. Shell Command Execution

**Severity**: 🟡 YELLOW in expected contexts (MCP bridging tools, CLI wrappers); 🔴 RED if remote content is executed
**Keywords**: `child_process`, `exec(`, `spawn(`, `popen`, `subprocess`, `system(`, backtick execution
**Trigger**: Shell execution where the command string includes remote/user-controlled content without sanitization.

## 7. Persistence Mechanisms

**Severity**: 🔴 RED
**Keywords**: `.bashrc`, `.zshrc`, `.profile`, `crontab`, `launchd`, `systemd`, `startup`, `rc.d`, `~/.config/autostart`
**Trigger**: Any code that writes to shell init files or registers as a system startup service without disclosure.

## 8. Runtime Secondary Download

**Severity**: 🔴 RED
**Keywords**: `subprocess.run(["pip"`, `subprocess.run(["npm"`, `child_process.exec("npm install"`, `curl … | bash`, install scripts calling remote `VERSION` or `MANIFEST` endpoints
**Trigger**: Installing undeclared additional packages during runtime, or fetching and executing remote scripts after initial install.

## 9. Auto-Update Mechanisms

**Severity**: 🔴 RED
**Keywords**: `fetch(VERSION_URL)`, `curl $MANIFEST`, file replacement via remote pull, background update daemon
**Trigger**: Code that silently replaces local files by polling a remote URL — creates a remote code execution channel if the upstream is compromised.

## 10. Code Obfuscation

**Severity**: 🔴 RED — treat as hiding malicious intent until proven otherwise
**Keywords**: `atob(`, `Buffer.from(..., 'base64')`, hex-encoded strings, minified one-liners with `eval`, packed JS (`p,a,c,k,e,d`)
**Trigger**: Any obfuscation in install scripts or startup code that prevents static review.

## 11. Process and System Reconnaissance

**Severity**: 🟡 YELLOW in isolation; 🔴 RED if followed by network exfiltration
**Keywords**: `whoami`, `hostname`, `uname`, `ps aux`, `netstat`, `ifconfig`, `/etc/passwd`, `os.getlogin()`
**Trigger**: Collecting system identity or process information, especially as a first step before network calls.

## 12. Zero-Width Unicode

**Severity**: 🔴 RED — used for steganographic hidden instructions
**Detection**: `grep -P '[\x{200B}\x{200C}\x{200D}\x{2063}\x{FEFF}]'`
**Trigger**: Any zero-width character in skill files, README, or package metadata.

---

## Behavioral Analysis Rules

Evaluate the **entire script as a whole**, not line by line:

- **Progressive escalation**: Scripts that start with benign operations (`whoami`, `df -h`) then escalate to credential harvesting. Judge by the combined net effect — one malicious step contaminates the whole script.
- **Mixed payloads**: Malicious commands hidden between legitimate ones. One harmful command makes the entire block suspect.
- **Comment/code mismatch**: Comments describe benign purpose while code does something different. Judge by code, not comments.
- **High-risk combinations**: shell + network + broad filesystem (especially with credential access) = 🔴 unless tightly scoped and clearly justified.
