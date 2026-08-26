# V22 Replay Report

Replay snapshots store event id, sequence, captured timestamp, payload and deterministic payload hash. Replay can iterate snapshots in event/sequence order and expose them through `/v22/replay/{event_id}`.

Controlled replay code tests PASS. Historical match replay from real provider data is NOT EXECUTED because no real feed snapshots exist in the environment.
