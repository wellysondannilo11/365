from __future__ import annotations
from abc import ABC, abstractmethod
import os, requests

class NotificationProvider(ABC):
    @abstractmethod
    def send(self,text:str)->bool: ...

class NullProvider(NotificationProvider):
    enabled=False
    def send(self,text): return False

class TelegramProvider(NotificationProvider):
    def __init__(self,token,chat_id,timeout=10): self.token=token;self.chat_id=chat_id;self.timeout=timeout
    @property
    def enabled(self): return bool(self.token and self.chat_id)
    def send(self,text):
        if not self.enabled:return False
        try:
            r=requests.post(f'https://api.telegram.org/bot{self.token}/sendMessage',data={'chat_id':self.chat_id,'text':text},timeout=self.timeout)
            r.raise_for_status(); return True
        except requests.RequestException:
            return False

def provider_from_env():
    token=os.getenv('TELEGRAM_BOT_TOKEN','');chat=os.getenv('TELEGRAM_CHAT_ID','')
    return TelegramProvider(token,chat) if token and chat else NullProvider()

def format_signal(item, *, status='PAPER / SHADOW'):
    return ('🔥 ROBO DA BET — NOVA OPORTUNIDADE\n'
            f"⚽ {item.get('event_name') or item.get('event_id')}\n"
            f"🏆 {item.get('league','—')}\n"
            f"⏱ {item.get('minute','PRE')}\n\n"
            f"Mercado: {item.get('market')} — {item.get('selection')}\n"
            f"Odd: {float(item.get('odds',0)):.2f}\n"
            f"Fair: {float(item.get('fair_odds',0)):.2f}\n"
            f"Edge: {float(item.get('edge',0))*100:+.1f}%\n"
            f"EV: {float(item.get('ev',0))*100:+.1f}%\n"
            f"Stake: {float(item.get('stake',0)):.2f}u\n"
            f"Status: 🟢 {status}")
