from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text, ForeignKey
from datetime import datetime
from backend.database import Base


# ============================
# USUARIOS
# ============================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    plan = Column(String, default="free")  # free / pro / advanced
    subscription_status = Column(String, default="inactive")

    analyses_used = Column(Integer, default=0)
    analyses_limit = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)


# ============================
# ANALISIS GLOBAL
# ============================

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    analysis_key = Column(String, unique=True, index=True)
    url = Column(String, index=True)
    content_hash = Column(String, index=True)

    structural_index = Column(Float)
    emotional_index = Column(Float)
    polarization_index = Column(Float)

    full_text = Column(Text)

    engine_version = Column(String(20))
    prompt_version = Column(String(20))

    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)


# ============================
# RELACION USUARIO - ANALISIS
# ============================

class UserAnalysis(Base):
    __tablename__ = "user_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    analysis_id = Column(Integer, ForeignKey("analyses.id"))

    created_at = Column(DateTime, default=datetime.utcnow)


# ============================
# LOG INTERNO (OPCIONAL)
# ============================

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


# ============================
# EXTENSIONES AUTORIZADAS
# ============================

class Extension(Base):
    __tablename__ = "extensions"

    id = Column(Integer, primary_key=True, index=True)

    extension_id = Column(String, unique=True, index=True, nullable=False)

    is_active = Column(Boolean, default=True)

    plan = Column(String, default="free")  # free / pro / enterprise

    analyses_used = Column(Integer, default=0)
    analyses_limit = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)