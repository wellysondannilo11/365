# V22 Security Audit

- Provider secrets are read from environment variables.
- Telegram token remains environment-only and is not exposed by API responses.
- `.env` is ignored by Git.
- No bookmaker execution endpoint was added.
- Provider HTTP errors are sanitized in API responses.
- Real credentials were not placed in the archive.

Residual limitations: Spring authentication remains the existing optional API-key filter; a full dependency CVE scan and runtime penetration test were not executed in this environment.
