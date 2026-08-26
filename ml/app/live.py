import math
from .features import temperature

def _poisson_cdf(lam,k):
    if k<0:return 0.0
    return sum(math.exp(-lam)*lam**i/math.factorial(i) for i in range(k+1))

def live_signal(m,line,side,pre_match_probability=None):
    rem=max(0,90-m.minute);temp=temperature(m)
    sample=m.shots+m.shots_on_target+m.big_chances+m.corners+round((m.xg_home+m.xg_away)*4)
    if m.minute<15 or sample<8:return {'eligible':False,'reason':'LIVE_SAMPLE_TOO_SMALL','temperature':temp}
    observed_rate=(m.xg_home+m.xg_away)/max(m.minute/90,.1); baseline=.9; pressure=(temp/100)*.35
    remaining_xg=max(.03,(observed_rate*.55+baseline*.45)*(rem/90)*(1+pressure))
    if pre_match_probability is not None: remaining_xg=.7*remaining_xg+.3*max(.03,pre_match_probability*2*(rem/90))
    current=m.home_goals+m.away_goals; stable=temp>=45 and sample>=8
    if side=='OVER':
        needed=max(0,int(line)+1-current);p=1-_poisson_cdf(remaining_xg,needed-1) if needed else 1.
    else:
        allowed=int(line)-1-current;p=_poisson_cdf(remaining_xg,allowed) if allowed>=0 else 0.
    return {'eligible':stable,'reason':'OK' if stable else 'LIVE_SIGNAL_UNSTABLE','temperature':temp,'remaining_xg':remaining_xg,'probability':max(0,min(1,p)),'sample':sample,'minutes_remaining':rem}
