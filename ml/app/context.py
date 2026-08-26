from dataclasses import dataclass
@dataclass
class MatchContext:
    home_advantage: float=1.0
    rivalry: float=0.0
    importance: float=0.0
    weather_penalty: float=0.0
    rest_balance: float=0.0

def context_multiplier(c:MatchContext):
    # Small bounded adjustment; context never overrides the market/value engine.
    return max(.92,min(1.08,1+0.025*c.home_advantage+0.02*c.rivalry+0.03*c.importance-0.02*c.weather_penalty+0.01*c.rest_balance))
