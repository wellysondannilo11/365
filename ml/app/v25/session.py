from __future__ import annotations
from datetime import datetime, timezone
import os,uuid,hashlib,json
from ..v22.providers import OddsAPIProvider,normalize_odds_api
from ..v21.realtime import FeedHealth
from ..v19.pricing import poisson_scoreline_distribution
from ..v20.stake import StakePolicy,size_stake
from ..v20.risk import PortfolioRisk,PortfolioLimits
from .dataset import V25Dataset
from .market_expression import MarketExpressionEngine
from .price_discovery import PriceDiscovery
from .policy import EntryPolicy
from .position import reassess,reversal
from .watchlist import Watchlist
from .notifications import TelegramNotificationProvider,NullNotificationProvider,format_decision,notification_id
from .observability import V25Observability
from .persistence import PostgreSQLV25Store, V25SnapshotStore

class V25Session:
    def __init__(self,provider=None,dataset=None,notifier=None,persistence=None,snapshot_store=None):
        self.provider=provider or OddsAPIProvider()
        self.persistence=persistence
        if self.persistence is None and os.getenv("DATABASE_URL"):
            self.persistence=PostgreSQLV25Store(); self.persistence.connect(); self.persistence.ensure_schema()
        self.dataset=dataset or V25Dataset(persistence=self.persistence)
        self.snapshot_store=snapshot_store or V25SnapshotStore(self.persistence)
        self.session_id=str(uuid.uuid4());self.kill=False;self.kill_reason=None
        self.health=FeedHealth(self.provider.name,max_age_seconds=float(os.getenv("FEED_STALE_SECONDS","30")),delayed_after_seconds=float(os.getenv("FEED_DELAYED_SECONDS","10")))
        self.engine=MarketExpressionEngine(
            float(os.getenv("MIN_ODDS","1.50")),
            float(os.getenv("PREFERRED_ODDS","1.66")),
            float(os.getenv("MIN_EDGE","0.05")),
            float(os.getenv("MIN_EV","0.05")),
            float(os.getenv("MAX_UNCERTAINTY","0.12")),
            float(os.getenv("EXCEPTION_EDGE","0.10")),
        )
        self.entry_policy=EntryPolicy(self.engine.min_odds,self.engine.preferred_odds,float(os.getenv("EXCEPTION_EDGE","0.10")),self.engine.min_edge,self.engine.min_ev,self.engine.max_uncertainty)
        self.stake_policy=StakePolicy(float(os.getenv("FRACTIONAL_KELLY","0.25")),float(os.getenv("MAX_STAKE_UNITS","1")),float(os.getenv("MIN_STAKE_UNITS","0.10")),float(os.getenv("BANKROLL_UNITS","50")))
        self.prices=PriceDiscovery();self.positions={};self.watchlist=Watchlist();self.observability=V25Observability();
        self.portfolio=PortfolioRisk(PortfolioLimits(max_per_event=float(os.getenv('MAX_EVENT_EXPOSURE_UNITS','1')),max_per_day=int(os.getenv('MAX_TIPS_PER_DAY','3')),max_simultaneous=float(os.getenv('MAX_SIMULTANEOUS_EXPOSURE_UNITS','5')),daily_stop=float(os.getenv('DAILY_STOP_UNITS','-4')),loss_streak_limit=int(os.getenv('LOSS_STREAK_COOLDOWN','3'))));self.notifier=notifier or (TelegramNotificationProvider() if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID") else NullNotificationProvider())
        self._restore_operational_state()
    def poll(self):
        if self.kill:return {"status":"KILL_SWITCH","events":[],"odds":[]}
        if not self.provider.configured:raise RuntimeError("CREDENTIALS_UNAVAILABLE")
        t0=datetime.now(timezone.utc)
        try:
            events,meta=self.provider.fetch_events_odds()
        except Exception:
            self.observability.inc("provider_errors")
            raise
        received_at=datetime.now(timezone.utc)
        self.observability.observe_ms("provider_latency",(received_at-t0).total_seconds())
        rows=normalize_odds_api(events,received_at)
        # The Odds API returns current/live and upcoming events on the odds endpoint.
        # Scores are fetched only when at least one event has reached commence time,
        # so LIVE state is derived from a real score feed rather than inferred from time alone.
        scores=[]
        now=received_at
        if any((self._parse_dt(e.get("commence_time")) or now) <= now for e in events):
            try:
                scores=self.provider.fetch_scores(days_from=1) or []
            except Exception:
                self.observability.inc("provider_errors")
                scores=[]
        score_map={str(x.get("id")):x for x in scores if x.get("id")}
        valid=[]; source_times=[]
        for r in rows:
            source_dt=self._parse_dt(r.get("source_timestamp"))
            if source_dt is None or source_dt > received_at:
                self.observability.inc("snapshots_rejected");self.observability.inc("PIT_rejections")
                continue
            event=next((e for e in events if str(e.get("id"))==str(r.get("event_id"))),{})
            score=score_map.get(str(r.get("event_id")))
            live=bool(score and not score.get("completed"))
            r["received_at"]=received_at.isoformat()
            r["decision_timestamp"]=received_at.isoformat()
            r["mode"]="LIVE" if live else "PRE"
            r["phase"]=r["mode"]
            r["score"] = self._score_payload(score) if score else None
            r["minute"] = self._extract_minute(score) if score else None
            r["snapshot_id"]=hashlib.sha256(f'{r["event_id"]}|{r["source_timestamp"]}|{r["bookmaker"]}|{r["market"]}|{r["selection"]}|{r["line"]}|{r["odds"]}'.encode()).hexdigest()[:32]
            r["price_movement"]=self.prices.observe(r)
            age=(received_at-source_dt).total_seconds()
            r["feed_age_seconds"]=age
            r["pit_valid"]=age >= 0 and source_dt <= received_at
            # A stale observation is never eligible for a decision, but is still retained
            # in the raw snapshot store for forensic completeness.
            if age > float(os.getenv("FEED_STALE_SECONDS","30")):
                r["quality_status"]="STALE";self.observability.inc("stale_feed")
            else:
                r["quality_status"]="PASS"
            try:self.snapshot_store.append(r)
            except Exception:self.observability.inc("snapshots_rejected")
            valid.append(r);source_times.append(source_dt)
        self.observability.inc("events_seen",len(events));self.observability.inc("snapshots_received",len(rows));self.observability.inc("events_valid",len({r.get("event_id") for r in valid}))
        agg=self.prices.aggregate(valid)
        for r in valid:r["market_aggregate"]=agg.get((str(r.get("event_id")),str(r.get("market")),r.get("line"),str(r.get("selection"))),{})
        newest=max(source_times) if source_times else None
        if newest:self.health.observe(newest,received_at)
        else:self.health.status=self.health.status.BLOCKED
        return {"session_id":self.session_id,"captured_at":received_at.isoformat(),"received_at":received_at.isoformat(),"events":events,"odds":valid,"health":self.health.status.value,"meta":meta,"scores":scores,"observability":self.observability.snapshot()}

    @staticmethod
    def _parse_dt(value):
        if not value:return None
        try:
            d=datetime.fromisoformat(str(value).replace("Z","+00:00"));return d if d.tzinfo else None
        except Exception:return None

    @staticmethod
    def _score_payload(score):
        if not score:return None
        vals=score.get("scores") or []
        return {"completed":bool(score.get("completed")),"last_update":score.get("last_update"),"scores":vals,"home_team":score.get("home_team"),"away_team":score.get("away_team")}

    @staticmethod
    def _extract_minute(score):
        if not score:return None
        raw=score.get("minute",score.get("clock"))
        try:return int(raw) if raw is not None else None
        except Exception:return None

    def scan(self,feed,mode="SHADOW",distribution_by_event=None):
        mode=mode.upper()
        if mode not in {"PAPER","SHADOW"}:raise ValueError("MODE_MUST_BE_PAPER_OR_SHADOW")
        now=datetime.now(timezone.utc); rows=feed.get("odds",[]); ranked=[]
        if feed.get("health")!="FEED_ONLINE":
            self.observability.inc("signals_rejected",len(rows));self.observability.inc("no_bet",len(rows))
            for r in rows: self._record(r,mode,"NO BET",0,"FEED_NOT_HEALTHY")
            return {"decision":"NO BET","reason":"FEED_NOT_HEALTHY","opportunities":[],"observability":self.observability.snapshot()}
        eligible=[]
        for r in rows:
            if not r.get("pit_valid") or r.get("quality_status")!="PASS":
                self.observability.inc("snapshots_rejected");self.observability.inc("PIT_rejections")
                self._record(r,mode,"NO BET",0,"PIT_OR_STALE_DATA")
            else:
                eligible.append(r)
        by_event={}
        for r in eligible:by_event.setdefault(str(r.get("event_id")),[]).append(r)
        selected=[]
        actual_selected=[]
        for event_id,group in by_event.items():
            d=(distribution_by_event or {}).get(event_id)
            if d is not None and not isinstance(d,list):d=poisson_scoreline_distribution(**d)
            t0=datetime.now(timezone.utc)
            result=self.engine.select(group,d,max_per_event=1)
            self.observability.observe_ms("pricing_latency",(datetime.now(timezone.utc)-t0).total_seconds())
            ranked.extend(result[0]);selected.extend(result[1])
            selected_keys={(x["bookmaker"],x["market"],x["selection"],x.get("line")) for x in result[1]}
            for x in result[0]:
                action="BET" if (x["bookmaker"],x["market"],x["selection"],x.get("line")) in selected_keys else x["decision"]
                stake=0.0
                if action=="BET" and x.get("edge") is not None:
                    stake=size_stake(float(x["probability"]),float(x["odds"]),policy=self.stake_policy,edge=float(x["edge"]),uncertainty=float(x["uncertainty"]))
                    if stake<=0:
                        action="NO BET";x["reason"]="RISK_LIMIT"
                    elif not self.portfolio.allowed(now,str(event_id),stake):
                        action="NO BET";x["reason"]="PORTFOLIO_RISK_LIMIT";stake=0.0
                    else:
                        self.portfolio.open(str(event_id),stake)
                recorded=self._record({**x,"snapshot_id":next((r.get("snapshot_id") for r in group if str(r.get("market")).upper().replace("-","_")==str(x.get("market")).upper().replace("-","_") and str(r.get("bookmaker"))==str(x.get("bookmaker")) and r.get("selection")==x.get("selection") and r.get("line")==x.get("line") and float(r.get("odds",0))==float(x.get("odds",0))),None)},mode,action,x.get("stake_units",stake),x.get("reason"),x)
                if action=="BET": actual_selected.append(recorded)
        selected=actual_selected
        self.observability.inc("signals_created",len(ranked));self.observability.inc("bets_selected",len(selected));self.observability.inc("no_bet",sum(x.get("decision")=="NO BET" for x in ranked))
        self.observability.inc("positions_open",len(selected))
        return {"session_id":self.session_id,"decision_id":str(uuid.uuid4()),"opportunities":ranked,"selected":selected,"no_bet_count":sum(x.get("decision")=="NO BET" for x in ranked),"scientific_status":"NOT_DETERMINED","observability":self.observability.snapshot()}
    def _record(self,r,mode,decision,stake,reason,extra=None):
        x=dict(r); x['phase']=x.get('phase') or ('LIVE' if x.get('minute') is not None else 'PRE')
        x['mode']='PAPER' if mode=='PAPER' else 'SHADOW'; x['decision']=decision
        x.setdefault("decision_time",datetime.now(timezone.utc).isoformat())
        x.setdefault("source_timestamp",x.get("available_at"))
        stable_identity={k:x.get(k) for k in ('event_id','snapshot_id','market','selection','line','odds','bookmaker','mode','decision')}
        did=hashlib.sha256(json.dumps(stable_identity,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()[:32];x.setdefault("match_id",x.get("event_id"));x.setdefault("provider_event_id",x.get("event_id"));x.setdefault("config_version","v25-default");x.update({"decision_id":did,"decision":decision,"mode":"PAPER" if mode=="PAPER" else "SHADOW","stake_units":stake,"reason":reason,"model_version":"MODEL_SUPPLIED" if x.get("model_probability") is not None else "MARKET_ONLY_BASELINE","feature_version":"v25","pricing_version":"MarketExpressionEngine-v25","position_state":"OPEN" if decision=="BET" else "NONE"})
        if extra:x.update({k:extra.get(k) for k in ("probability","fair_odds","edge","ev","score","uncertainty","market_quality")})
        if decision=="BET":
            pid=str(uuid.uuid4());x["position_id"]=pid;x["position_state"]="OPEN";x["opened_at"]=datetime.now(timezone.utc).isoformat();self.positions[pid]=dict(x)
        recorded=self.dataset.append(x)
        if decision in {"BET","HOLD","REDUCE","EXIT","REVERSE"}:
            self.notifier.send(format_decision(recorded),notification_id(recorded))
        return recorded
    def _restore_operational_state(self):
        """Rebuild open PAPER/SHADOW positions and daily risk counters after restart."""
        try: rows=self.dataset.rows()
        except Exception:return
        if not rows:return
        settled_ids={str(r.get("position_id")) for r in rows if r.get("event_type")=="SETTLEMENT" and r.get("position_id")}
        open_rows=[r for r in rows if r.get("decision")=="BET" and r.get("position_id") and str(r.get("position_id")) not in settled_ids]
        self.positions={str(r["position_id"]):dict(r) for r in open_rows}
        now=datetime.now(timezone.utc); self.portfolio.reset(now)
        day=now.astimezone(timezone.utc).date().isoformat()
        todays=[r for r in rows if str(r.get("created_at","")).startswith(day)]
        self.portfolio.state.tips_taken=sum(1 for r in todays if r.get("decision")=="BET")
        self.portfolio.state.open_exposure=sum(float(r.get("stake_units") or 0) for r in open_rows)
        for r in open_rows:self.portfolio.state.event_exposure[str(r.get("event_id"))]=self.portfolio.state.event_exposure.get(str(r.get("event_id")),0)+float(r.get("stake_units") or 0)
        settled=[r for r in todays if r.get("event_type")=="SETTLEMENT" and r.get("pnl_units") is not None]
        self.portfolio.state.daily_pnl=sum(float(r.get("pnl_units") or 0) for r in settled)
        self.portfolio.state.loss_streak=0
        for r in sorted(settled,key=lambda x:x.get("created_at","")):
            self.portfolio.state.loss_streak=self.portfolio.state.loss_streak+1 if float(r.get("pnl_units") or 0)<0 else 0

    def live_reprice(self,event_id,minute,home_goals,away_goals,home_xg,away_xg,market_rows,remaining_xg=False):
        minute=int(minute)
        if minute < 0 or minute > 130: raise ValueError("INVALID_LIVE_MINUTE")
        rem=max(.01,(90-minute)/90)
        # By default xG inputs are treated as cumulative observed xG. A provider may
        # explicitly mark them as remaining expected goals with remaining_xg=True.
        hl=max(0.0,float(home_xg)) if remaining_xg else max(0.0,float(home_xg))*rem
        al=max(0.0,float(away_xg)) if remaining_xg else max(0.0,float(away_xg))*rem
        d0=poisson_scoreline_distribution(hl,al)
        # Convert remaining-goal distribution into a final-score distribution.
        d=[]
        for s in d0:
            d.append(type(s)(int(home_goals)+s.home_goals,int(away_goals)+s.away_goals,s.probability))
        markets=[dict(x,live=True,event_id=event_id) for x in market_rows]
        ranked,selected=self.engine.select(markets,d,1)
        return {"event_id":event_id,"minute":minute,"state":{"home_goals":home_goals,"away_goals":away_goals,"home_xg":home_xg,"away_xg":away_xg,"remaining_xg_mode":bool(remaining_xg)},"markets":ranked,"best":selected[0] if selected else None}
    def manage_position(self,position,current_odds,fair_probability):return reassess(position["entry_odds"],current_odds,fair_probability)
    def settle_position(self,position_id,result,closing_odds,pnl_units,clv_value=None):
        if position_id not in self.positions: raise KeyError("POSITION_NOT_FOUND")
        p=self.positions[position_id];p.update({"position_state":"SETTLED","closed_at":datetime.now(timezone.utc).isoformat(),"result":result,"closing_odds":closing_odds,"pnl_units":pnl_units,"clv":clv_value})
        self.observability.inc("positions_closed"); self.portfolio.close(str(p.get('event_id')),float(p.get('stake_units') or 0),float(pnl_units),datetime.now(timezone.utc))
        settlement=dict(p);settlement.update({"event_type":"SETTLEMENT","decision":"EXIT","decision_id":str(uuid.uuid4()),"reason":"POSITION_SETTLED","stake_units":p.get("stake_units",0),"mode":p.get("mode","PAPER")})
        self.dataset.append(settlement)
        return p
    def reversal(self,current_odds,current_probability):
        out=reversal(current_odds,current_probability,float(os.getenv("MIN_EDGE","0.05")))
        if out.action=="REVERSE": self.observability.inc("reversals")
        return out
