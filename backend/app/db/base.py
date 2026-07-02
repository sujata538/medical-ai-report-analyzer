"""
Declarative base for all SQLAlchemy ORM models.

Importing `Base` from a single place (rather than each model creating its
own) is what lets Alembic autogenerate migrations correctly, and lets
`init_db.create_all()` see every model as long as it has been imported
somewhere before this runs (see app/models/__init__.py).
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models in the application."""
    pass
