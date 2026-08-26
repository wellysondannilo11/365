from __future__ import annotations
import requests
import pandas as pd

class TheOddsAPI:
    name='the-odds-api'
    def __init__(self,key,timeout=30): self.key=key; self.timeout=timeout
    def _get(self,path,**params):
        r=requests.get(f'https://api.the-odds-api.com/v4/{path.lstrip("/")}',params={'apiKey':self.key,**params},timeout=self.timeout,headers={'User-Agent':'RoboDaBet/V18'})
        r.raise_for_status(); return r.json()
    def soccer_odds(self,sport='soccer_epl',regions='eu',markets='h2h,totals'):
        return self._get(f'sports/{sport}/odds',regions=regions,markets=markets,oddsFormat='decimal')
    def historical_soccer_odds(self,sport='soccer_epl',date=None,regions='eu',markets='h2h,totals'):
        if not date: raise ValueError('HISTORICAL_DATE_REQUIRED')
        return self._get(f'historical/sports/{sport}/odds',regions=regions,markets=markets,oddsFormat='decimal',date=date)
    def historical_events(self,sport='soccer_epl',date=None):
        if not date: raise ValueError('HISTORICAL_DATE_REQUIRED')
        return self._get(f'historical/sports/{sport}/events',date=date)
    def historical_event_odds(self,event_id,sport='soccer_epl',date=None,regions='eu',markets='h2h,totals'):
        if not date: raise ValueError('HISTORICAL_DATE_REQUIRED')
        if not event_id: raise ValueError('HISTORICAL_EVENT_ID_REQUIRED')
        return self._get(f'historical/sports/{sport}/events/{event_id}/odds',regions=regions,markets=markets,oddsFormat='decimal',date=date)
    @staticmethod
    def normalize_historical_response(payload, source='the-odds-api'):
        if not isinstance(payload, dict): raise ValueError('INVALID_HISTORICAL_ODDS_PAYLOAD')
        snapshot=payload.get('timestamp') or payload.get('snapshot_timestamp')
        if not snapshot: raise ValueError('HISTORICAL_ODDS_SNAPSHOT_TIMESTAMP_REQUIRED')
        snapshot=pd.Timestamp(snapshot,tz='UTC') if pd.Timestamp(snapshot).tzinfo is None else pd.Timestamp(snapshot).tz_convert('UTC')
        rows=[]
        data=payload.get('data', payload.get('events', []))
        if isinstance(data,dict): data=[data]
        for event in data:
            event_id=event.get('id')
            if not event_id: continue
            event_time=event.get('commence_time')
            for book in event.get('bookmakers', []):
                bookmaker=book.get('key') or book.get('title') or 'unknown'
                book_update=book.get('last_update')
                book_ts=pd.to_datetime(book_update,utc=True,errors='coerce') if book_update else pd.NaT
                for market in book.get('markets', []):
                    market_key=market.get('key') or market.get('market') or 'unknown'
                    market_update=market.get('last_update')
                    market_ts=pd.to_datetime(market_update,utc=True,errors='coerce') if market_update else pd.NaT
                    # The API guarantees the returned object represents the state at
                    # the provider snapshot. Keep snapshot and inner update clocks
                    # separately; PIT uses the provider snapshot, never kickoff.
                    # `snapshot` is the provider-selected historical state clock.
                    # Nested bookmaker/market `last_update` fields describe updates
                    # inside the returned object and are NOT the snapshot selector.
                    # Do not reject a valid historical snapshot because a nested
                    # update clock is later than the selected snapshot. PIT uses
                    # snapshot/source_timestamp <= decision_time.
                    for outcome in market.get('outcomes', []):
                        price=outcome.get('price')
                        if price is None: continue
                        rows.append({'event_id':str(event_id),'event_time':event_time,'bookmaker':str(bookmaker),'market':str(market_key),'selection':str(outcome.get('name') or 'unknown'),'line':outcome.get('point'),'price':price,'captured_at':snapshot,'snapshot_timestamp':snapshot,'bookmaker_last_update':book_ts,'market_last_update':market_ts,'source_timestamp':snapshot,'available_at':snapshot,'source':source,'source_record_id':f'{event_id}:{bookmaker}:{market_key}:{outcome.get("name")}:{snapshot.isoformat()}'})
        d=pd.DataFrame(rows)
        if d.empty:return d
        for c in ('event_time','captured_at','snapshot_timestamp','bookmaker_last_update','market_last_update','source_timestamp','available_at'):
            if c in d: d[c]=pd.to_datetime(d[c],utc=True,errors='coerce')
        if d[['captured_at','source_timestamp','available_at']].isna().any().any(): raise ValueError('INVALID_PROVIDER_TIMESTAMP')
        d['raw_hash']=d.apply(lambda r: __import__('hashlib').sha256(r.to_json().encode()).hexdigest(),axis=1)
        return d
