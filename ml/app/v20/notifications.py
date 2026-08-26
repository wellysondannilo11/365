from abc import ABC,abstractmethod
import requests
class NotificationProvider(ABC):
    @abstractmethod
    def send(self,text:str)->bool: ...
class NullProvider(NotificationProvider):
    def send(self,text): return False
class TelegramProvider(NotificationProvider):
    def __init__(self,token,chat_id,timeout=15): self.token=token;self.chat_id=chat_id;self.timeout=timeout
    @property
    def enabled(self): return bool(self.token and self.chat_id)
    def send(self,text):
        if not self.enabled:return False
        r=requests.post(f'https://api.telegram.org/bot{self.token}/sendMessage',data={'chat_id':self.chat_id,'text':text},timeout=self.timeout);r.raise_for_status();return True
def provider_from_env():
    import os
    return TelegramProvider(os.getenv('TELEGRAM_BOT_TOKEN',''),os.getenv('TELEGRAM_CHAT_ID',''))
