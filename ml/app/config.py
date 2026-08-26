from dataclasses import dataclass
import os
from dotenv import load_dotenv
load_dotenv()
@dataclass(frozen=True)
class Settings:
    bankroll: float = float(os.getenv('BANKROLL_UNITS','50'))
    min_odds: float = float(os.getenv('MIN_ODDS','1.50'))
    min_edge: float = float(os.getenv('MIN_EDGE','0.05'))
    min_ev: float = float(os.getenv('MIN_EV','0.05'))
    min_dq: float = float(os.getenv('MIN_DQ','80'))
    daily_stop: float = float(os.getenv('DAILY_STOP_UNITS','-4'))
    loss_cooldown: int = int(os.getenv('LOSS_STREAK_COOLDOWN','3'))
    fractional_kelly: float = float(os.getenv('FRACTIONAL_KELLY','0.25'))
    max_stake: float = float(os.getenv('MAX_STAKE_UNITS','1'))
    paper: bool = os.getenv('PAPER','true').lower() == 'true'
    postgres_url: str = os.getenv('DATABASE_URL','')
    redis_url: str = os.getenv('REDIS_URL','redis://redis:6379/0')
    telegram_token: str = os.getenv('TELEGRAM_BOT_TOKEN','')
    telegram_chat_id: str = os.getenv('TELEGRAM_CHAT_ID','')
    unit_brl: float = float(os.getenv('UNIT_BRL','500'))
    preferred_odds: float = float(os.getenv('PREFERRED_ODDS','1.66'))
    max_tips_per_event: int = int(os.getenv('MAX_TIPS_PER_EVENT','1'))
    max_tips_per_day: int = int(os.getenv('MAX_TIPS_PER_DAY','3'))
    max_simultaneous_positions: int = int(os.getenv('MAX_SIMULTANEOUS_POSITIONS','5'))
settings=Settings()
