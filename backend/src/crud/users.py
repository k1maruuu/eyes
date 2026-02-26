from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import hash_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def create(self, db: Session, obj_in: UserCreate) -> User:
        if db.query(User).filter(User.email == obj_in.email).one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        data = obj_in.model_dump()
        password = data.pop("password")
        data["hashed_password"] = hash_password(password)
        obj = User(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        data = obj_in.model_dump(exclude_unset=True)
        if "password" in data and data["password"]:
            db_obj.hashed_password = hash_password(data.pop("password"))
        for k, v in data.items():
            setattr(db_obj, k, v)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_crud = CRUDUser(User)