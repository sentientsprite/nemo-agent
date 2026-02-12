# Security Policy

If you believe you've found a security issue in NEMO, please report it privately.

## Reporting

Report vulnerabilities directly to the repository where the issue lives:

- **Core CLI and gateway** — [nemo/nemo](https://github.com/nemo/nemo)
- **macOS desktop app** — [nemo/nemo](https://github.com/nemo/nemo) (apps/macos)
- **iOS app** — [nemo/nemo](https://github.com/nemo/nemo) (apps/ios)
- **Android app** — [nemo/nemo](https://github.com/nemo/nemo) (apps/android)
- **NEMOHub** — [nemo/nemohub](https://github.com/nemo/nemohub)
- **Trust and threat model** — [nemo/trust](https://github.com/nemo/trust)

For issues that don't fit a specific repo, or if you're unsure, email **security@nemo.ai** and we'll route it.

For full reporting instructions see our [Trust page](https://trust.nemo.ai).

### Required in Reports

1. **Title**
2. **Severity Assessment**
3. **Impact**
4. **Affected Component**
5. **Technical Reproduction**
6. **Demonstrated Impact**
7. **Environment**
8. **Remediation Advice**

Reports without reproduction steps, demonstrated impact, and remediation advice will be deprioritized. Given the volume of AI-generated scanner findings, we must ensure we're receiving vetted reports from researchers who understand the issues.

## Security & Trust

**Jamieson O'Reilly** ([@theonejvo](https://twitter.com/theonejvo)) is Security & Trust at NEMO. Jamieson is the founder of [Dvuln](https://dvuln.com) and brings extensive experience in offensive security, penetration testing, and security program development.

## Bug Bounties

NEMO is a labor of love. There is no bug bounty program and no budget for paid reports. Please still disclose responsibly so we can fix issues quickly.
The best way to help the project right now is by sending PRs.

## Out of Scope

- Public Internet Exposure
- Using NEMO in ways that the docs recommend not to
- Prompt injection attacks

## Operational Guidance

For threat model + hardening guidance (including `nemo security audit --deep` and `--fix`), see:

- `https://docs.nemo.ai/gateway/security`

### Web Interface Safety

NEMO's web interface is intended for local use only. Do **not** bind it to the public internet; it is not hardened for public exposure.

## Runtime Requirements

### Node.js Version

NEMO requires **Node.js 22.12.0 or later** (LTS). This version includes important security patches:

- CVE-2025-59466: async_hooks DoS vulnerability
- CVE-2026-21636: Permission model bypass vulnerability

Verify your Node.js version:

```bash
node --version  # Should be v22.12.0 or later
```

### Docker Security

When running NEMO in Docker:

1. The official image runs as a non-root user (`node`) for reduced attack surface
2. Use `--read-only` flag when possible for additional filesystem protection
3. Limit container capabilities with `--cap-drop=ALL`

Example secure Docker run:

```bash
docker run --read-only --cap-drop=ALL \
  -v nemo-data:/app/data \
  nemo/nemo:latest
```

## Security Scanning

This project uses `detect-secrets` for automated secret detection in CI/CD.
See `.detect-secrets.cfg` for configuration and `.secrets.baseline` for the baseline.

Run locally:

```bash
pip install detect-secrets==1.5.0
detect-secrets scan --baseline .secrets.baseline
```
