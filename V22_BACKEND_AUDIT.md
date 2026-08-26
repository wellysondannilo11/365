# V22 Backend Audit

**Status:** PARTIAL/PASS for code-level integration; runtime build BLOCKED by missing Maven in the audit environment.

The Spring Boot backend remains a compatibility/API proxy and now exposes V22 status, feed poll, scan, metrics, dataset and position endpoints. Python FastAPI remains the domain/research engine. The API imports and route registration were tested with FastAPI TestClient.

Runtime HTTP smoke tests passed for `/health`, `/v22/status`, `/v22/metrics`, `/v22/dataset`. `/v22/feed/poll` and `/v22/scan` correctly return a safe 503 when credentials are unavailable.

Maven compilation/startup was **NOT EXECUTED — Maven unavailable**.
