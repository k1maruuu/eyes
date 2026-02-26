from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.token import TokenOut
from src.core.jwt import create_access_token
from src.core.security import verify_password
from src.core.config import settings
from src.models.user import User

router = APIRouter()


@router.post("/login", response_model=TokenOut)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).one_or_none()

    # Не раскрываем, существует ли email (защита от user enumeration)
    if not user:
        # Можно добавить небольшую искусственную задержку, но это опционально
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    now = datetime.now(timezone.utc)

    # 1) Проверка блокировки
    if getattr(user, "locked_until", None) and user.locked_until > now:
        # не говорим "заблокирован", просто запрещаем
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many attempts. Try later.")

    # 2) Проверка пароля
    if not verify_password(password, user.hashed_password):
        user.login_attempts = (user.login_attempts or 0) + 1

        # Если превышен лимит — блокируем на N минут
        if user.login_attempts >= settings.LOGIN_MAX_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
            user.login_attempts = 0  # можно обнулить, чтобы считать по окнам блокировки

        db.add(user)
        db.commit()

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # 3) Успешный логин: сброс счётчика и блокировки
    user.login_attempts = 0
    user.locked_until = None
    user.last_login_at = now
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.email, "role": user.role.value})
    return TokenOut(access_token=token)