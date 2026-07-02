"""
Generic repository base class implementing the Repository Pattern.

Concrete repositories subclass this with a specific SQLAlchemy model to get
CRUD operations for free, while still being free to add domain-specific
query methods of their own.
"""
from typing import Generic, TypeVar, Type, Optional, List

from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id_: str) -> Optional[ModelType]:
        return self.db.get(self.model, id_)

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: ModelType) -> ModelType:
        self.db.add(obj_in)
        self.db.commit()
        self.db.refresh(obj_in)
        return obj_in

    def update(self, db_obj: ModelType, updates: dict) -> ModelType:
        for field, value in updates.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: ModelType) -> None:
        self.db.delete(db_obj)
        self.db.commit()
