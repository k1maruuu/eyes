from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.token import TokenOut
from src.core.jwt import create_access_token
from src.core.security import verify_password
from src.core.config import settings
from src.models.user import User

router = APIRouter()

@router.post("/login", response_model=TokenOut)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm использует поле username (туда кладём email)
    email = form_data.username
    password = form_data.password

    user = db.query(User).filter(User.email == email).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    now = datetime.now(timezone.utc)

    if user.locked_until and user.locked_until > now:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many attempts. Try later.")

    if not verify_password(password, user.hashed_password):
        user.login_attempts = (user.login_attempts or 0) + 1
        if user.login_attempts >= settings.LOGIN_MAX_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
            user.login_attempts = 0
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user.login_attempts = 0
    user.locked_until = None
    user.last_login_at = now
    db.commit()

    token = create_access_token({"sub": user.email, "role": user.role.value})
    return TokenOut(access_token=token)

# Заглушка для ESIA gosuslugi
# @router.post("/esia")
# def esia_login(data: EsiaLoginIn, db: Session = Depends(get_db)):
#     user = user_crud.get_by_email(db, email=data.email)
#     if not user:
#         raise HTTPException(401, "Unknown user")
#     token = create_access_token({"sub": str(user.id), "role": user.role.value})
#     return {"access_token": token, "token_type": "bearer"}