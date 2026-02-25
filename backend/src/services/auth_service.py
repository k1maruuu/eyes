from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.user import User
from src.core.security import verify_password, create_access_token

def login(db: Session, email: str, password: str) -> str:
    user = db.query(User).filter(User.email == email).one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
    return create_access_token(subject=user.email, role=user.role.value)