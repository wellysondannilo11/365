from dataclasses import dataclass
from enum import Enum
class HoldoutState(str,Enum): RESEARCH='RESEARCH';FREEZE='FREEZE';HOLDOUT_LOCKED='HOLDOUT_LOCKED';FINAL_EVALUATION='FINAL_EVALUATION'
@dataclass
class HoldoutGuard:
    state:HoldoutState=HoldoutState.RESEARCH
    def freeze(self): self.state=HoldoutState.FREEZE
    def lock(self):
        if self.state!=HoldoutState.FREEZE: raise RuntimeError('HOLDOUT_REQUIRES_FREEZE')
        self.state=HoldoutState.HOLDOUT_LOCKED
    def final(self):
        if self.state!=HoldoutState.HOLDOUT_LOCKED: raise RuntimeError('HOLDOUT_NOT_LOCKED')
        self.state=HoldoutState.FINAL_EVALUATION
    def assert_research_access(self):
        if self.state in (HoldoutState.HOLDOUT_LOCKED,HoldoutState.FINAL_EVALUATION): raise RuntimeError('HOLDOUT_LOCKED')
