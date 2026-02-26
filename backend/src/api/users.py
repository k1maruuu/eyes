from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.user import UserCreate, UserUpdate, UserOut
from src.crud.users import user_crud
from src.services.deps import require_roles

router = APIRouter()

@router.post("/", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    return user_crud.create(db, data)

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    obj = user_crud.get(db, user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="User not found")
    return obj

@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    obj = user_crud.get(db, user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.update(db, obj, data)