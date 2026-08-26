# ENTITY RESOLUTION REPORT V4

The canonical backbone remains at 7,570 unique match IDs and 387 teams. No new remote entities were acquired in this execution because DNS/network access is blocked.

Existing team canonicalization is preserved. V4 adds explicit source-state controls and keeps player/venue/bookmaker registries ready for future acquisition.

Rules:
- no string-only promotion to a canonical entity;
- aliases require evidence;
- men's, women's, youth and reserve teams remain separate;
- unresolved conflicts remain unresolved instead of being guessed.
