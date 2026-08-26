from __future__ import annotations
import pandas as pd
THRESHOLD=0.02
HYPOTHESIS_ID='H005_CROSS_BOOK_DISPERSION_V1'

def evaluate_h005(df:pd.DataFrame):
    required={'event_id','bookmaker','market','selection','odds','reference_odds','pit_status','opening_semantics'}
    missing=sorted(required-set(df.columns))
    if missing: raise ValueError(f'MISSING_H005_COLUMNS:{missing}')
    d=df.copy(); d=d[d.pit_status.eq('EXACT_PIT')]
    if d.empty: return d, {'hypothesis_id':HYPOTHESIS_ID,'threshold':THRESHOLD,'reference':'Average opening','entry':'Bet365 opening','status':'NO_EXACT_PIT'}
    d=d[d.opening_semantics.eq('EXPLICIT_OPENING')]
    if d.empty: return d, {'hypothesis_id':HYPOTHESIS_ID,'threshold':THRESHOLD,'reference':'Average opening','entry':'Bet365 opening','status':'NO_EXPLICIT_OPENING'}
    d['bookmaker_norm']=d.bookmaker.astype(str).str.casefold()
    keys=['event_id','market','selection']
    ref=d[d.bookmaker_norm.eq('average')][keys+['odds']].rename(columns={'odds':'reference_odds_calculated'})
    ent=d[d.bookmaker_norm.eq('bet365')][keys+['odds']].rename(columns={'odds':'entry_odds'})
    x=ent.merge(ref,on=keys,how='inner')
    if x.empty: return x, {'hypothesis_id':HYPOTHESIS_ID,'threshold':THRESHOLD,'reference':'Average opening','entry':'Bet365 opening','status':'NO_MATCHING_REFERENCE_ENTRY'}
    x['relative_price']=x.entry_odds/x.reference_odds_calculated-1
    x=x[x.relative_price>=THRESHOLD].copy(); x['hypothesis_id']=HYPOTHESIS_ID; x['threshold']=THRESHOLD
    x['reference_odds']=x.reference_odds_calculated
    return x.reset_index(drop=True), {'hypothesis_id':HYPOTHESIS_ID,'threshold':THRESHOLD,'reference':'Average opening','entry':'Bet365 opening','status':'CANDIDATES' if not x.empty else 'NO_SIGNAL','candidate_rows':len(x)}
