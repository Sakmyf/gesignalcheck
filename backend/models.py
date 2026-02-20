from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Date
from datetime import datetime, date
from database import Base

class AnalysisLog(Base):
    __tablename__ = "analysis_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    trust_score = Column(Float)
    rhetorical_score = Column(Float)
    narrative_score = Column(Float)
    absence_score = Column(Float)

    risk_index = Column(Float, index=True)
    level = Column(String(20), index=True)

    premium_requested = Column(Boolean, default=False)
    engine_version = Column(String(20))

class DailyMetrics(Base):
    __tablename__ = "daily_metrics"
    
    date = Column(Date, primary_key=True, default=date.today)
    total_verifications = Column(Integer, default=0)
    total_premium_reports = Column(Integer, default=0)
    average_risk = Column(Float, default=0.0)

class AnonymousEvent(Base):
    __tablename__ = "anonymous_events"
    
    id = Column(Integer, primary_key=True)
    event_name = Column(String(50), index=True)
    country = Column(String(2), index=True)
    user_type = Column(String(10), default="free", index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)