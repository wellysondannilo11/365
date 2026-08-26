# ROBO DA BET V18 — SOURCE AUDIT

## Executed source assessment

V18 reviewed the source classes required by the research specification and attempted acquisition in the actual runtime.

| Source | Class | Intended use | V18 execution |
|---|---|---|---|
| The Odds API | A | provider timestamped historical bookmaker snapshots | NOT AVAILABLE — no API key; runtime DNS unavailable |
| Betfair Historical Data | A | timestamped Exchange back/lay/volume | NOT AVAILABLE — no purchased package/credentials |
| Football-Data.co.uk | B/C | real results/stats and bounded pre-closing/closing odds | ATTEMPTED; blocked by runtime DNS |
| StatsBomb Open Data | C/D | football event/lineup features | ATTEMPTED conceptually; runtime network unavailable |
| Flashscore | D | complementary context | NOT USED; no reproducible PIT acquisition path and no bypass attempted |

## External source verification

The current Football-Data documentation states that it provides historical results, match statistics and betting odds, and that since 2019/20 it has collected a pre-closing set and a closing set of odds. It also states that those collections occur at specified fixture times rather than providing a provider-native snapshot for every decision instant. V18 therefore keeps Football-Data in the B/C class rather than silently promoting it to strict PIT odds.

The Odds API documentation states that historical odds are snapshots and that the historical endpoint returns the closest snapshot equal to or earlier than the requested timestamp. Historical access is paid. This is compatible with the V18 strict PIT design, subject to credentials and actual acquisition.

Betfair's developer documentation describes its Historical Data service as timestamped Exchange data available for purchase/download. This is compatible with strict PIT research when the purchased data is present.

## Decision

The strict betting research gate remains closed until class-A provider-native timestamped odds are actually acquired and validated.
