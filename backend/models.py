from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from datetime import datetime
from database import Base


class AnalysisLog(Base):
    __tablename__ = "analysis_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    trust_score = Column(Float)
    rhetorical_score = Column(Float)
    narrative_score = Column(Float)
    absence_score = Column(Float)

    risk_index = Column(Float)
    level = Column(String(20))

    premium_requested = Column(Boolean, default=False)

    engine_version = Column(String(20))
