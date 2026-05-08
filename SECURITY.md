# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| latest (`main`) | ✅ |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, report them via email to **ryanjbush@gmail.com** with the subject line `[SECURITY] Astra AI — <brief description>`.

Include:
- A description of the vulnerability and its potential impact
- Steps to reproduce
- Any suggested remediation if known

You can expect an acknowledgement within **48 hours** and a resolution timeline within **7 days** for critical issues.

## API Key Safety

This project requires external API keys (search, LLM providers). **Never commit API keys to this repository.** Use `.env` files (excluded from version control via `.gitignore`) or environment variables. If you believe a key has been accidentally committed, rotate it immediately and notify via the contact above.

## Scope

This project is a portfolio/demonstration platform. It is not deployed as a public service.
