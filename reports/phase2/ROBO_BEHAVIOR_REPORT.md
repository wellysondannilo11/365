# ROBO BEHAVIOR REPORT — PHASE 2

The current real-data materialization does **not** contain enough decision-time odds/features to reconstruct historical Robo BET/NO_BET/WATCH/WAIT decisions for the full 40-match set without fabricating inputs. Therefore: 

- BET = 0 observed historical Robo decisions
- NO_BET = 0 observed historical Robo decisions
- WATCH = 0 observed historical Robo decisions
- WAIT_FOR_PRICE = 0 observed historical Robo decisions

This is deliberately **not** interpreted as "the Robo never bets". It means the required historical decision state is not present in the materialized dataset.

The 10-match 1X2 market-only pilot is a baseline experiment, not a Robo signal experiment.
