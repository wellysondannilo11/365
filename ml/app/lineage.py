from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any
from .temporal import assert_point_in_time
@dataclass(frozen=True)
class FeatureLineage:
    feature_name:str;feature_version:str;entity:str;event_id:str;as_of:datetime;available_at:datetime;source:str;lineage:str
    source_time:datetime|None=None;ingested_at:datetime|None=None;source_record_ids:tuple[str,...]=()
    def validate(self): assert_point_in_time(self.available_at,self.as_of)
    def to_dict(self)->dict[str,Any]:return asdict(self)
