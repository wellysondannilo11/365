import numpy as np

def psi(expected,actual,bins=10):
    expected=np.asarray(expected);actual=np.asarray(actual);qs=np.linspace(0,1,bins+1);edges=np.unique(np.quantile(expected,qs))
    if len(edges)<3:return 0.0
    e,_=np.histogram(expected,edges);a,_=np.histogram(actual,edges);e=(e+1)/sum(e+1);a=(a+1)/sum(a+1)
    return float(np.sum((a-e)*np.log(a/e)))

def drift_status(value,warning=.1,critical=.25): return 'CRITICAL' if value>=critical else 'WARNING' if value>=warning else 'OK'
