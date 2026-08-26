from pathlib import Path
import json
from ml.app.research.global_expansion import build_route_registry, build_coverage, attempt_registry, inventory_local_real, write_outputs
ROOT=Path(__file__).resolve().parents[1]
registry=build_route_registry()
before=inventory_local_real(ROOT)
coverage=build_coverage(ROOT,registry)
attempts,network=attempt_registry(ROOT,registry)
web_sources=[
 {'source':'Football-Data.co.uk','url':'https://www.football-data.co.uk/all_new_data.php','status':'SOURCE_CONFIRMED_NOT_MATERIALIZED'},
 {'source':'Football-Data.co.uk','url':'https://www.football-data.co.uk/downloadm.php','status':'SOURCE_CONFIRMED_NOT_MATERIALIZED'},
 {'source':'StatsBomb Open Data','url':'https://github.com/statsbomb/open-data','status':'SOURCE_CONFIRMED_NOT_MATERIALIZED'},
 {'source':'The Odds API','url':'https://the-odds-api.com/historical-odds-data/','status':'SOURCE_CONFIRMED_CREDENTIAL_REQUIRED'},
 {'source':'Sportmonks','url':'https://www.sportmonks.com/football-api/','status':'SOURCE_CONFIRMED_CREDENTIAL_REQUIRED'},
]
summary=write_outputs(ROOT,attempts,coverage,before,web_sources)
summary['network']=network
(ROOT/'reports/expansion/EXPANSION_EXECUTION.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(summary,indent=2,ensure_ascii=False))
