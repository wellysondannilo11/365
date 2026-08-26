"""V6 resumable acquisition entry point. Never promotes discovery to materialization."""
from pathlib import Path
import os, json
from providers.footballcsv_squads import download_team
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'data/raw/acquisition_worker'
MAN=ROOT/'data/global_dataset/registry/GLOBAL_ACQUISITION_MANIFEST_V6.json'

def main():
    MAN.parent.mkdir(parents=True,exist_ok=True); state={'version':'6.0','real_money':'DISABLED','artifacts':[]}
    if MAN.exists():
        try: state=json.loads(MAN.read_text())
        except Exception: pass
    existing={x.get('url') for x in state.get('artifacts',[])}
    for team in ('flamengo','palmeiras'):
        url='https://raw.githubusercontent.com/footballcsv/cache.footballsquads/master/'+('brazil/2024/seriea/flamengo.txt' if team=='flamengo' else 'brazil/2024/seriea/palmeir.txt')
        if url in existing: continue
        try: state['artifacts'].append(download_team(team,RAW/f'v6_{team}_squad.txt'))
        except Exception as e: state['artifacts'].append({'team':team,'url':url,'state':'BLOCKED','error':f'{type(e).__name__}: {e}'})
    MAN.write_text(json.dumps(state,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(state,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
