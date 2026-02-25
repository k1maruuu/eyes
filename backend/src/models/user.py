from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as En

from ..database import Base


class UserRole(str, En):
    ADMIN = "admin"
    FELDSHER = "feldsher"
    SURGEON = "surgeon"
    PATIENT = "patient"  # опционально; чаще пациент = отдельная сущность + токен портала


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(255), nullable=False)

    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(64), nullable=True, index=True)

    hashed_password = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), default=UserRole.FELDSHER, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    login_attempts = Column(Integer, default=0, nullable=False)

    # Telegram: лучше chat_id (username может меняться)
    telegram_chat_id = Column(String(64), nullable=True)
    telegram_username = Column(String(64), nullable=True)

    # Привязка к ЛПУ/району
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="users")

    reviews = relationship("Review", back_populates="surgeon", cascade="all,delete", passive_deletes=True)
    comments = relationship("Comment", back_populates="author", cascade="all,delete", passive_deletes=True)
    uploaded_files = relationship("FileAsset", back_populates="uploaded_by", cascade="all,delete", passive_deletes=True)
    ops = relationship("OperationLog", back_populates="user", cascade="all,delete", passive_deletes=True)