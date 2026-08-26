# V21 TELEGRAM REPORT

`NotificationProvider` and `TelegramProvider` are environment-secret based.

Missing `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID` produces a disabled/null provider and does not break selection, ledger or paper/shadow operation.

Unit tests for missing credentials and signal formatting: **PASS**.

Real Telegram delivery: **NOT EXECUTED** — credentials unavailable.
