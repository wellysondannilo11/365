from sqlalchemy import create_engine,String,Float,Integer,DateTime,Boolean,Text,JSON
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,sessionmaker
from .config import settings
class Base(DeclarativeBase):pass
class Bet(Base):
 __tablename__='bets';id:Mapped[str]=mapped_column(String(128),primary_key=True);event_id:Mapped[str]=mapped_column(String(128),index=True);league:Mapped[str]=mapped_column(String(128),index=True);market:Mapped[str]=mapped_column(String(64),index=True);selection:Mapped[str]=mapped_column(String(128));odds:Mapped[float]=mapped_column(Float);probability:Mapped[float]=mapped_column(Float);fair_odds:Mapped[float]=mapped_column(Float);edge:Mapped[float]=mapped_column(Float);ev:Mapped[float]=mapped_column(Float);stake:Mapped[float]=mapped_column(Float);status:Mapped[str]=mapped_column(String(16),default='OPEN');pnl:Mapped[float]=mapped_column(Float,default=0);closing_odds:Mapped[float|None]=mapped_column(Float,nullable=True);clv:Mapped[float|None]=mapped_column(Float,nullable=True);created_at:Mapped[DateTime]=mapped_column(DateTime);live:Mapped[bool]=mapped_column(Boolean,default=False);reason:Mapped[str]=mapped_column(Text,default='')
class Decision(Base):
 __tablename__='decisions';id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True);event_id:Mapped[str]=mapped_column(String(128),index=True);decision:Mapped[str]=mapped_column(String(16));reason:Mapped[str]=mapped_column(Text);score:Mapped[float]=mapped_column(Float);created_at:Mapped[DateTime]=mapped_column(DateTime)
class FeatureRecord(Base):
 __tablename__='feature_lineage';id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True);event_id:Mapped[str]=mapped_column(String(128),index=True);feature_name:Mapped[str]=mapped_column(String(128));feature_version:Mapped[str]=mapped_column(String(32));available_at:Mapped[DateTime]=mapped_column(DateTime);as_of:Mapped[DateTime]=mapped_column(DateTime);source:Mapped[str]=mapped_column(String(128));lineage:Mapped[str]=mapped_column(Text)
class ModelRun(Base):
 __tablename__='model_runs';id:Mapped[str]=mapped_column(String(128),primary_key=True);market:Mapped[str]=mapped_column(String(64));model_type:Mapped[str]=mapped_column(String(64));status:Mapped[str]=mapped_column(String(32));metrics:Mapped[dict]=mapped_column(JSON);created_at:Mapped[DateTime]=mapped_column(DateTime)
try:
    engine=create_engine(settings.postgres_url,pool_pre_ping=True);SessionLocal=sessionmaker(bind=engine,expire_on_commit=False)
except Exception:
    engine=None;SessionLocal=None
def init_db():
    if engine is None:return False
    Base.metadata.create_all(engine);return True
