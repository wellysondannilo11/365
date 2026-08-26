import math
import numpy as np
from scipy.optimize import minimize

def poisson_pmf(k,lam): return math.exp(-lam)*lam**k/math.factorial(k)
def poisson_ou_probability(lam, line, over=True):
    threshold=int(math.floor(line))+1 if over else int(math.floor(line))
    if over: return 1-sum(poisson_pmf(k,lam) for k in range(threshold))
    return sum(poisson_pmf(k,lam) for k in range(threshold))
def dixon_coles_adjust(h,a,rho=-0.08):
    # Low-score correction used as a multiplicative likelihood adjustment.
    if h==0 and a==0:return 1-rho
    if h==0 and a==1:return 1+rho
    if h==1 and a==0:return 1+rho
    if h==1 and a==1:return 1-rho
    return 1.0

def dixon_coles_goal_rates(home_xg,away_xg,home_adv=0.12): return max(.05,home_xg+home_adv),max(.05,away_xg)
def elo_expected(home_elo,away_elo,home_adv=55): return 1/(1+10**(-((home_elo+home_adv)-away_elo)/400))
