import requests
class APIFootballAdapter:
    name='api-football'
    def __init__(self,key):self.key=key
    def fixtures(self,league,season):
        r=requests.get('https://v3.football.api-sports.io/fixtures',params={'league':league,'season':season},headers={'x-apisports-key':self.key},timeout=30);r.raise_for_status();return r.json()
