import argparse, os, time
from app.v22.providers import OddsAPIProvider
from app.v22.manager import FeedManagerV22
from app.v22.dataset import ResearchDataset

def main():
    p=argparse.ArgumentParser(description='Robo da Bet V23 real-feed PAPER/SHADOW observer')
    p.add_argument('--mode',choices=['PAPER','SHADOW'],default='SHADOW'); p.add_argument('--poll-seconds',type=float,default=30); p.add_argument('--once',action='store_true')
    a=p.parse_args(); provider=OddsAPIProvider();
    if not provider.configured: raise SystemExit('BLOCKED_EXTERNAL_DEPENDENCY:CREDENTIALS_UNAVAILABLE')
    manager=FeedManagerV22(provider=provider)
    while True:
        result=__import__('app.v22.api_ext',fromlist=['scan']).scan(a.mode)
        print(result,flush=True)
        if a.once: break
        time.sleep(max(1,a.poll_seconds))
if __name__=='__main__': main()
