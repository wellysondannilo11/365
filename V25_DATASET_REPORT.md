# V25 Dataset Report

V25 adds `robo_bet_dataset_v25.jsonl` with append-only hash chaining.

Important fields include event, match, provider, bookmaker, market, line, selection, snapshot, observation, decision, source timestamp, capture time, fair probability/odds, edge, EV, model/feature/pricing versions, stake, position state, result, closing odds and CLV.

Tamper test passed: changing an existing decision invalidates the chain.

Real dataset size in this runtime: **0 real observations / 0 real settled bets**.
