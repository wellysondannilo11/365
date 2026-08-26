# V21 DATA QUALITY REPORT

Fail-closed controls added/preserved:

- missing timestamps;
- timezone-naive decision time;
- future data;
- stale live feed;
- stale live odds;
- invalid odds;
- low data quality;
- PIT violation.

Feed states: ONLINE, DELAYED, STALE, OFFLINE, DATA QUALITY BLOCK.

No timestamp is silently replaced by ingestion time, kickoff or current time.
