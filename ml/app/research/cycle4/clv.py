from __future__ import annotations
import pandas as pd

def calculate_clv(entry_price, closing_price, entry_timestamp=None, closing_timestamp=None):
    if entry_price is None or closing_price is None: return None, 'CLV_UNAVAILABLE'
    try: e=float(entry_price); c=float(closing_price)
    except (TypeError,ValueError): return None,'CLV_INVALID'
    if e<=1 or c<=1: return None,'CLV_INVALID'
    if entry_timestamp is not None and closing_timestamp is not None:
        et=pd.to_datetime(entry_timestamp,utc=True,errors='coerce'); ct=pd.to_datetime(closing_timestamp,utc=True,errors='coerce')
        if pd.isna(et) or pd.isna(ct) or ct < et: return None,'CLV_INVALID'
    return e/c-1.0,'CLV_AVAILABLE'
