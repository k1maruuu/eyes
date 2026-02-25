from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.token import TokenOut
from src.core.jwt import create_access_token
from src.core.security import verify_password
from src.models.user import User

router = APIRouter()

@router.post("/login", response_model=TokenOut)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email, "role": user.role.value})
    return TokenOut(access_token=token)