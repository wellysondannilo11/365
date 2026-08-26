from __future__ import annotations

def settle_decimal(entry_price, stake, outcome):
    if entry_price is None or stake is None or outcome not in {'WIN','LOSS','PUSH','VOID'}:
        raise ValueError('INVALID_SETTLEMENT')
    p=float(entry_price); s=float(stake)
    if p<=1 or s<0: raise ValueError('INVALID_SETTLEMENT_PRICE_OR_STAKE')
    if outcome=='WIN': pnl=s*(p-1)
    elif outcome in {'PUSH','VOID'}: pnl=0.0
    else: pnl=-s
    return {'outcome':outcome,'profit_units':pnl,'stake_units':s,'roi':pnl/s if s else None}
