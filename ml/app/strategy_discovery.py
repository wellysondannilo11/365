from dataclasses import dataclass, asdict
import math
@dataclass
class Experiment:
    experiment_id:str; features:str; threshold:float; market:str; league:str; period:str; n_trials:int=1; holdout_locked:bool=True
class DiscoveryLog:
    def __init__(self): self.items=[]
    def add(self,e:Experiment): self.items.append(asdict(e))
    def bonferroni_alpha(self,alpha=.05): return alpha/max(1,sum(x['n_trials'] for x in self.items))
