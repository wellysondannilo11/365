from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class Fold:
    train_start:str; train_end:str; validation_start:str; validation_end:str; test_start:str; test_end:str
    train_end_idx:int|None=None; validation_start_idx:int|None=None; validation_end_idx:int|None=None; test_start_idx:int|None=None; test_end_idx:int|None=None
    train_events:int=0; validation_events:int=0; test_events:int=0


def _utc(x):
    t=pd.Timestamp(x)
    return t.tz_localize('UTC') if t.tzinfo is None else t.tz_convert('UTC')


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    if 'event_id' not in df.columns:
        raise ValueError('EVENT_ID_REQUIRED')
    if 'event_time' not in df.columns:
        raise ValueError('EVENT_TIME_REQUIRED')
    d=df.copy()
    d['_event_time_utc']=pd.to_datetime(d.event_time,utc=True,errors='coerce')
    if d['_event_time_utc'].isna().any():
        raise ValueError('INVALID_EVENT_TIME')
    # An event is the atomic temporal unit. Rows belonging to one event may not
    # be split merely because the dataset contains multiple markets/bookmakers.
    event_times=d.groupby(d.event_id.astype(str),sort=False)['_event_time_utc'].agg(['min','max'])
    if (event_times['min']!=event_times['max']).any():
        bad=event_times[event_times['min']!=event_times['max']].index.tolist()[:5]
        raise ValueError(f'EVENT_ID_HAS_MULTIPLE_EVENT_TIMES:{bad}')
    return d.sort_values(['_event_time_utc','event_id'],kind='stable').reset_index(drop=True)


def _event_ranges(d: pd.DataFrame):
    ids=d.event_id.astype(str).to_numpy()
    if len(ids)==0:return []
    ranges=[]; start=0
    for i in range(1,len(ids)):
        if ids[i]!=ids[i-1]:
            ranges.append((ids[start],start,i))
            start=i
    ranges.append((ids[start],start,len(ids)))
    return ranges


def assert_no_event_overlap(parts):
    seen=set()
    for name,df in parts.items():
        if 'event_id' not in df: continue
        ids=set(df.event_id.astype(str)); overlap=seen & ids
        if overlap: raise ValueError(f'EVENT_SPLIT_LEAKAGE:{name}:{sorted(overlap)[:5]}')
        seen |= ids


def split_by_event_groups(df, train_end, val_end, test_end, holdout_start=None):
    d=_prepare(df)
    times=d['_event_time_utc']; te,ve,xe=map(_utc,(train_end,val_end,test_end))
    event_anchor=d.groupby(d.event_id.astype(str))['_event_time_utc'].transform('first')
    train=d[event_anchor<=te].drop(columns=['_event_time_utc'])
    val=d[(event_anchor>te)&(event_anchor<=ve)].drop(columns=['_event_time_utc'])
    test=d[(event_anchor>ve)&(event_anchor<=xe)].drop(columns=['_event_time_utc'])
    hold=d[event_anchor>xe].drop(columns=['_event_time_utc']) if holdout_start is None else d[event_anchor>=_utc(holdout_start)].drop(columns=['_event_time_utc'])
    assert_no_event_overlap({'train':train,'validation':val,'test':test,'holdout':hold})
    return train,val,test,hold


def nested_walk_forward(df, min_train=100, validation=30, test=30, gap=0, embargo=0, holdout=0.15):
    d=_prepare(df); ranges=_event_ranges(d); n_events=len(ranges)
    if n_events==0:return [],d.iloc[:0].copy(),d.iloc[:0].copy()
    hold_n=max(1,int(n_events*holdout)); research_event_count=n_events-hold_n
    if research_event_count<=0:return [],d.iloc[:0].copy(),d.copy()
    research=d.iloc[:ranges[research_event_count-1][2]].copy()
    hold=d.iloc[ranges[research_event_count][1]:].copy()
    folds=[]; cursor=min_train
    while cursor+gap+validation+embargo+test<=research_event_count:
        tr_range=ranges[:cursor]
        val_start=cursor+gap; val_end=val_start+validation
        test_start=val_end+embargo; test_end=test_start+test
        tr=research.iloc[tr_range[0][1]:tr_range[-1][2]]
        va=research.iloc[ranges[val_start][1]:ranges[val_end-1][2]]
        te=research.iloc[ranges[test_start][1]:ranges[test_end-1][2]]
        assert_no_event_overlap({'train':tr,'validation':va,'test':te,'holdout':hold})
        folds.append(Fold(str(tr.event_time.min()),str(tr.event_time.max()),str(va.event_time.min()),str(va.event_time.max()),str(te.event_time.min()),str(te.event_time.max()),int(tr_range[-1][2]),int(ranges[val_start][1]),int(ranges[val_end-1][2]),int(ranges[test_start][1]),int(ranges[test_end-1][2]),cursor,validation,test))
        cursor=test_end
    return folds,research,hold


def assert_same_event_not_split(df,parts):
    owners={}
    for name,part in parts.items():
        for eid in part.event_id.astype(str):
            if eid in owners and owners[eid]!=name: raise ValueError(f'SAME_EVENT_SPLIT:{eid}:{owners[eid]}:{name}')
            owners[eid]=name
