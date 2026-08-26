# V22 Realtime Report

The realtime architecture is now capable of acquiring current odds through the authorized provider adapter, normalizing them, storing snapshots, producing replay snapshots and passing a market-only baseline into the existing V21 selective decision engine.

The real-feed path is blocked until a valid provider credential is supplied. This is intentional and visible through status endpoints.
