# Source Trust Signals

Before deep-diving into code, assess publisher/source credibility. These are high-weight signals:

- **Official organization**: Published under a recognized org scope (`@modelcontextprotocol/*`, `@types/*`, `pallets/*`, `tokio-rs/*`, etc.). These are examples of strong trust signals, not a whitelist.
- **Verified publisher**: npm verified publisher badge, PyPI trusted publisher, crates.io verified owner
- **Metadata consistency**: Does the registry's `repository` field point to a real GitHub repo? Do the README, homepage, and publisher align? Mismatches are 🟡.
- **Maintainer history**: Maintainer has other established packages, account is not newly created
- **Star jacking**: A fork of a popular repo can inherit the original's star count. If a GitHub repo shows high stars but the org/user doesn't match the expected upstream, check if it's a fork. Cross-reference stars against actual npm/pip download counts — a repo with 5,000 stars but 50 weekly downloads is suspicious.

Treat publisher/repository identity consistency as a primary trust signal. An inconsistency (e.g., `repository` points to a different org than the publisher) is always worth flagging. Official org scope is a strong positive signal, but never overrides malicious install behavior or metadata inconsistencies — always check install hooks regardless of publisher reputation.
