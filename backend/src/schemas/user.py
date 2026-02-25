from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime

from src.schemas.common import ORMBase
from src.models.user import UserRole
from src.core.validators import normalize_phone

class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone_number: Optional[str] = Field(default=None, max_length=64)
    password: str = Field(min_length=6, max_length=128)

    role: UserRole = UserRole.FELDSHER
    organization_id: Optional[int] = None

    telegram_chat_id: Optional[str] = Field(default=None, max_length=64)
    telegram_username: Optional[str] = Field(default=None, max_length=64)

    @field_validator("phone_number")
    @classmethod
    def _phone(cls, v):
        if not v:
            return None
        return normalize_phone(v)

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(default=None, max_length=64)

    password: Optional[str] = Field(default=None, min_length=6, max_length=128)

    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    organization_id: Optional[int] = None

    telegram_chat_id: Optional[str] = Field(default=None, max_length=64)
    telegram_username: Optional[str] = Field(default=None, max_length=64)

    @field_validator("phone_number")
    @classmethod
    def _phone(cls, v):
        if not v:
            return None
        return normalize_phone(v)

class UserOut(ORMBase):
    id: int
    full_name: str
    email: str
    phone_number: Optional[str] = None

    role: UserRole
    is_active: bool
    login_attempts: int

    telegram_chat_id: Optional[str] = None
    telegram_username: Optional[str] = None

    organization_id: Optional[int] = None

    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole