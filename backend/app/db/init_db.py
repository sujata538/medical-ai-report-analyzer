"""
Database initialization.

`init_db()` creates all tables (for local/dev use — in staging/production
Alembic migrations should be used instead) and seeds the default roles so
the app has something sensible to assign new users to.
"""
import logging

from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine, SessionLocal
# Import models so they're registered on Base.metadata before create_all()
from app.models import (  # noqa: F401
    user, role, report, uploaded_file, parameter,
    reference_range, recommendation, audit_log, user_session,
)

logger = logging.getLogger(__name__)

DEFAULT_ROLES = ["admin", "patient", "clinician"]


def create_all_tables() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created (if not already present).")


def seed_roles(db: Session) -> None:
    from app.models.role import Role

    for role_name in DEFAULT_ROLES:
        exists = db.query(Role).filter(Role.name == role_name).first()
        if not exists:
            db.add(Role(name=role_name))
    db.commit()
    logger.info("Default roles seeded: %s", DEFAULT_ROLES)


def init_db() -> None:
    create_all_tables()
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
