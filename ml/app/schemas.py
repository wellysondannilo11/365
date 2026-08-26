from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime, timezone

class MatchSnapshot(BaseModel):
    model_config=ConfigDict(extra='allow')
    event_id:str; league:str; home:str; away:str; kickoff:datetime; captured_at:datetime
    available_at:datetime|None=None; ingested_at:datetime|None=None; event_time:datetime|None=None; source_time:datetime|None=None; decision_time:datetime|None=None
    minute:int=0; home_goals:int=0; away_goals:int=0; xg_home:float=0.0; xg_away:float=0.0
    shots:int=0; shots_on_target:int=0; big_chances:int=0; dangerous_attacks:int=0; box_entries:int=0
    possession_home:float=50.0; ppda_home:float=10.0; corners:int=0; red_cards:int=0
    source:str='manual'; source_timestamp:Optional[datetime]=None
    def model_post_init(self, __context):
        object.__setattr__(self,'available_at',self.available_at or self.captured_at)
        object.__setattr__(self,'ingested_at',self.ingested_at or self.captured_at)
        object.__setattr__(self,'event_time',self.event_time or self.kickoff)
        object.__setattr__(self,'source_time',self.source_time or self.source_timestamp or self.captured_at)
        object.__setattr__(self,'decision_time',self.decision_time or self.captured_at)

class OddsSnapshot(BaseModel):
    event_id:str; market:str; selection:str; odds:float=Field(gt=1.0); bookmaker:str='unknown'; captured_at:datetime; source:str='manual'
    line:float|None=None; source_timestamp:datetime|None=None; available_at:datetime|None=None
    def model_post_init(self,__context):
        object.__setattr__(self,'available_at',self.available_at or self.captured_at)
        object.__setattr__(self,'source_timestamp',self.source_timestamp or self.captured_at)

class OpportunityRequest(BaseModel):
    match:MatchSnapshot; odds:list[OddsSnapshot]; pre_match_probabilities:dict[str,float]={}; model_probabilities:dict[str,float]={}
    decision_time:datetime|None=None

class Settlement(BaseModel):
    bet_id:str; result:Literal['WIN','LOSS','VOID']; closing_odds:Optional[float]=None

class PricingRequest(BaseModel):
    event_id: str
    decision_time: datetime
    home_expected_goals: float = Field(ge=0)
    away_expected_goals: float = Field(ge=0)
    market_state: Literal['PRE', 'LIVE'] = 'PRE'
    dixon_coles_rho: float | None = None
    max_goals: int = Field(default=10, ge=3, le=20)
