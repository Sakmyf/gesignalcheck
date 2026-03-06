import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ==========================================================
# DATABASE URL (ULTRA SAFE)
# ==========================================================

DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("DATABASE_PUBLIC_URL")
    or "postgresql://postgres:qpxfKApQOsYeHnuxmEAjwOPdNDnMtfTN@mainline.proxy.rlwy.net:40717/railway"
)

print("DATABASE_URL usada:", DATABASE_URL)

# ==========================================================
# ENGINE CONFIG
# ==========================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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