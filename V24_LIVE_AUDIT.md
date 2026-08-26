# V24 Live Audit

V24 adds a strict live snapshot ingestion boundary:
- event identity;
- captured timestamp;
- source timestamp;
- minute;
- score;
- xG and optional live statistics;
- stale-source blocking;
- future-data blocking;
- snapshot history per event.

Existing V20 live repricing/position logic remains preserved.

A real live provider/statistics session was not executed because provider credentials/runtime were unavailable.
