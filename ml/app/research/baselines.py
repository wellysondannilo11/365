from __future__ import annotations
import numpy as np

def implied_baseline(odds):
    odds=float(odds)
    if odds<=1: raise ValueError('INVALID_ODDS')
    return 1/odds

def historical_frequency(labels):
    x=np.asarray(labels,dtype=float)
    if len(x)==0: raise ValueError('EMPTY_LABELS')
    return float(x.mean())

def constant_baseline(labels): return historical_frequency(labels)
