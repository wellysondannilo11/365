from __future__ import annotations
import os,requests,hashlib,json
from pathlib import Path
import time
class NotificationProvider:
    def send(self,text:str,notification_id:str)->bool:raise RuntimeError('ABSTRACT_NOTIFICATION_PROVIDER')
class NullNotificationProvider(NotificationProvider):
    def send(self,text,notification_id):return False
class TelegramNotificationProvider(NotificationProvider):
    def __init__(self,token=None,chat_id=None,timeout=15):
        self.token=token or os.getenv('TELEGRAM_BOT_TOKEN','');self.chat_id=chat_id or os.getenv('TELEGRAM_CHAT_ID','');self.timeout=timeout
        self.sent_path=Path(os.getenv('TELEGRAM_SENT_IDS_PATH','artifacts/paper_trading/telegram_sent_ids.jsonl'));self.sent_path.parent.mkdir(parents=True,exist_ok=True);self.sent=set()
        if self.sent_path.exists():
            for line in self.sent_path.read_text(encoding='utf-8').splitlines():
                if line.strip(): self.sent.add(line.strip())
    @property
    def enabled(self):return bool(self.token and self.chat_id)
    def send(self,text,notification_id):
        if not self.enabled:return False
        if notification_id in self.sent:return True
        last=None
        for attempt in range(3):
            try:
                r=requests.post(f'https://api.telegram.org/bot{self.token}/sendMessage',data={'chat_id':self.chat_id,'text':text},timeout=self.timeout)
                r.raise_for_status()
                self.sent.add(notification_id)
                with self.sent_path.open('a',encoding='utf-8') as f:f.write(notification_id+'\n')
                return True
            except requests.RequestException as exc:
                last=exc
                if attempt<2: time.sleep(0.5*(2**attempt))
        if last: raise last
        return False
class FakeNotificationProvider(NotificationProvider):
    def __init__(self):self.messages=[];self.ids=set()
    def send(self,text,notification_id):
        if notification_id in self.ids:return True
        self.ids.add(notification_id);self.messages.append(text);return True

def format_decision(row):
    icon={'BET':'🟢','NO BET':'🔴','HOLD':'🟡','REDUCE':'🟠','EXIT':'🔴','REVERSE':'🔄'}.get(row.get('decision'),'ℹ️')
    phase='LIVE' if row.get('mode')=='LIVE' or row.get('minute') is not None else 'PRE'
    return f"{icon} {row.get('decision')}\nJogo: {row.get('event_name','')}\nLiga: {row.get('league','')}\nMercado: {row.get('market','')} {row.get('line','') or ''}\nSeleção: {row.get('selection','')}\nOdd: {row.get('odds','')}\nProbabilidade: {row.get('probability','')}\nFair: {row.get('fair_odds','')}\nEdge: {row.get('edge','')}\nEV: {row.get('ev','')}\nStake: {row.get('stake_units','')}U\nCasa: {row.get('bookmaker','')}\nModo: {row.get('mode','')}\nFase: {phase}\nMinuto: {row.get('minute','')}\nTimestamp: {row.get('decision_time') or row.get('created_at','')}\nMotivo: {row.get('reason','')}"

def notification_id(row):return hashlib.sha256(f"{row.get('decision_id')}|{row.get('decision')}".encode()).hexdigest()
