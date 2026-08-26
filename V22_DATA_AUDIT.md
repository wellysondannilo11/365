# V22 Data Audit

Concrete external adapter added: The Odds API v4. It uses environment credentials, timeout/retry behavior, decimal odds, bookmaker/market normalization and source timestamps. The provider is documented by the vendor as supplying current odds for live/upcoming events and historical odds on eligible plans. urlThe Odds API official documentationhttps://the-odds-api.com/

Real feed execution was **NOT EXECUTED — THE_ODDS_API_KEY unavailable**. The system returns `BLOCKED_EXTERNAL_DEPENDENCY:CREDENTIALS_UNAVAILABLE` instead of pretending to have real data.

Historical PIT backtest remains **NOT EXECUTED** because no real timestamped historical bookmaker dataset was available in the environment.
