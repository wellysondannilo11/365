# V17 — SECURITY AUDIT

## Findings

- No provider tokens were included in the V17 package.
- `.env.example` contains placeholders only.
- Docker Compose database credentials were removed from hardcoded values and changed to environment variables.
- ML default database URL no longer embeds a password.
- V17 acquisition logs record credential presence as boolean only; secret values are never logged.
- No real betting execution path was enabled.

## Runtime limitation

A complete container/runtime security assessment was not possible because Docker was unavailable.
