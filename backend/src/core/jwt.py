from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from src.core.config import settings
from src.schemas.token import TokenData

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def verify_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        email: str | None = payload.get("sub")
        if not email:
            return None
        role: str | None = payload.get("role")
        return TokenData(email=email, role=role)
    except JWTError:
        return None