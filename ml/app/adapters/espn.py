import requests
class ESPNAdapter:
    name='espn'
    def scoreboard(self,league='eng.1',dates=None):
        params={'limit':100};
        if dates: params['dates']=dates
        r=requests.get(f'https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard',params=params,timeout=20);r.raise_for_status();return r.json()
