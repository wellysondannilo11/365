from __future__ import annotations
from collections import Counter
import pandas as pd
from .exact_pit import classify_observation

def build_unified_pit(df:pd.DataFrame):
    exact=[]; reasons=Counter(); seen=set(); dup=0; non=0; invalid=0
    for row in df.to_dict('records'):
        r=classify_observation(row); reasons[r.reason]+=1
        if r.status=='NON_PIT': non+=1; continue
        if r.status=='PIT_INVALID': invalid+=1; continue
        if r.observation_id in seen: dup+=1; continue
        seen.add(r.observation_id); x=dict(row); x.update(r.to_dict()); exact.append(x)
    out=pd.DataFrame(exact)
    if not out.empty: out=out.drop_duplicates('observation_id').reset_index(drop=True)
    return out, {'input_rows':len(df),'exact_pit_observations':len(out),'exact_pit_events':int(out.event_id.nunique()) if not out.empty else 0,
                  'non_pit':non,'pit_invalid':invalid,'deduplicated':dup,'reason_counts':dict(reasons)}
