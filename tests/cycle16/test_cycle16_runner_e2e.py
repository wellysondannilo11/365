from pathlib import Path
import pandas as pd
from ml.scripts.run_cycle16 import run_cycle16


def test_runner_writes_required_artifacts_without_promoting_nonpit(tmp_path):
    p=tmp_path/'incoming.csv'
    pd.DataFrame([{
      'id':'1','sportsbook':'bet365','event_id':'e1','market_type':'moneyline','selection':'A','odds_decimal':2.1,
      'event_start_time':'2026-08-25T20:00:00Z','timestamp':'2026-08-25T18:00:00Z','is_live':False
    }]).to_csv(p,index=False)
    import json
    try:
        result=run_cycle16(p, tmp_path/'reports')
        status=json.loads((tmp_path/'reports/CYCLE16_PIT_STATUS.json').read_text())
        assert result['real_money']=='DISABLED'
        assert status['exact_pit_observations']==1
    finally:
        pass
