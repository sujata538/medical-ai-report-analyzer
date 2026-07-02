"""
Database engine + session factory.

Provides `get_db()`, a FastAPI dependency that yields a SQLAlchemy Session
and guarantees it is closed after the request, regardless of exceptions.
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# `check_same_thread` is only needed for SQLite (allows use across the
# thread pool FastAPI/Starlette uses for sync endpoints).
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a DB session, closes it when the request ends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
