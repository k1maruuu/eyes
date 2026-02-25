from typing import Any, Generic, Optional, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)

class CRUDBase(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelT]:
        return db.get(self.model, id)

    def create(self, db: Session, obj_in: CreateSchemaT) -> ModelT:
        obj = self.model(**obj_in.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, db_obj: ModelT, obj_in: UpdateSchemaT) -> ModelT:
        data = obj_in.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(db_obj, k, v)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: Any) -> Optional[ModelT]:
        obj = db.get(self.model, id)
        if not obj:
            return None
        db.delete(obj)
        db.commit()
        return obj