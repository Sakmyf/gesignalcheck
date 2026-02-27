import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ==========================================================
# DATABASE URL
# ==========================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada")

# ==========================================================
# ENGINE CONFIG
# ==========================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # evita conexiones muertas en Railway
    pool_size=10,
    max_overflow=20
)

# ==========================================================
# SESSION FACTORY
# ==========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ==========================================================
# BASE MODEL
# ==========================================================

Base = declarative_base()

# ==========================================================
# DEPENDENCY FOR FASTAPI
# ==========================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()