from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass(frozen=True)
class ImmutablePaperBet:
    signal_id: str
    event_id: str
    decision_time: str
    market: str
    selection: str
    line: float | None
    bookmaker: str
    entry_odds: float
    model_probability: float
    fair_odds: float | None
    market_probability: float | None
    edge: float
    ev: float
    model_version: str
    feature_version: str
    calibration_version: str | None
    dataset_fingerprint: str
    source_quality: str
    status: str = 'PAPER'

    def to_dict(self) -> dict:
        return asdict(self)


class ImmutablePaperLedger:
    def __init__(self, path='artifacts/paper_trading/v19_signals.jsonl'):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, signal: ImmutablePaperBet) -> dict:
        payload = signal.to_dict()
        with self.path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(payload, sort_keys=True, separators=(',', ':')) + '\n')
        return payload
