# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security & Compliance Architecture

RecoverAI is built with strict compliance guardrails:
1. **RBI Guidelines Compliance**: Automated enforcement of quiet hours (21:00 - 08:00 IST) suppressing customer communication.
2. **Credential Sanitization**: API keys (Razorpay, Gemini, OpenAI) are handled strictly via environment variables and never logged or serialized.
3. **Immutable Audit Trails**: Every recovery action is checked against compliance rules before dispatch and recorded in an immutable ledger.

## Reporting a Vulnerability

Please report sensitive security issues via private disclosure to maintain merchant data privacy.
