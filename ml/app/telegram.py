import requests
class Telegram:
    def __init__(self,token,chat_id):self.url=f'https://api.telegram.org/bot{token}/sendMessage' if token else '';self.chat_id=chat_id
    def send(self,text):
        if not self.url or not self.chat_id:return False
        r=requests.post(self.url,data={'chat_id':self.chat_id,'text':text},timeout=15);r.raise_for_status();return True
