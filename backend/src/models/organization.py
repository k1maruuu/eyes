from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)

    # ЛПУ/Организация/Район (упрощённо)
    name = Column(String(255), nullable=False, index=True)
    city = Column(String(128), nullable=True, index=True)
    region = Column(String(128), nullable=True, index=True)
    address = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    users = relationship("User", back_populates="organization", cascade="all,delete", passive_deletes=True)
    patients = relationship("Patient", back_populates="organization", cascade="all,delete", passive_deletes=True)