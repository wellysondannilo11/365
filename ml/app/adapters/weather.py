import requests
class OpenMeteoAdapter:
    name='open-meteo'
    def forecast(self,latitude,longitude,start_date,end_date):
        r=requests.get('https://api.open-meteo.com/v1/forecast',params={'latitude':latitude,'longitude':longitude,'hourly':'temperature_2m,precipitation,wind_speed_10m','start_date':start_date,'end_date':end_date,'timezone':'UTC'},timeout=20);r.raise_for_status();return r.json()
