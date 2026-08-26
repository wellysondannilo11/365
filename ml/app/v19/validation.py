from __future__ import annotations

import math
from typing import Iterable
import numpy as np


def validate_distribution(distribution: Iterable[dict]) -> dict:
    rows = list(distribution)
    probs = np.array([float(x['probability']) for x in rows], dtype=float)
    if len(probs) == 0:
        return {'status': 'FAIL', 'reason': 'EMPTY'}
    return {
        'status': 'PASS' if np.all(np.isfinite(probs)) and np.all(probs >= 0) and abs(probs.sum() - 1) <= 1e-8 else 'FAIL',
        'rows': int(len(probs)),
        'sum_probability': float(probs.sum()),
        'min_probability': float(probs.min()),
        'max_probability': float(probs.max()),
    }


def fair_odds_sanity(probability: float, fair_odds: float | None) -> bool:
    if probability <= 0:
        return fair_odds is None
    return fair_odds is not None and math.isclose(float(fair_odds), 1.0 / probability, rel_tol=1e-10, abs_tol=1e-10)
