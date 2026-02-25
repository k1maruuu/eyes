from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class FileAsset(Base):
    __tablename__ = "file_assets"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    checklist_item_id = Column(Integer, ForeignKey("patient_checklist_items.id", ondelete="SET NULL"), nullable=True, index=True)

    # S3/MinIO key/path
    storage_key = Column(String(512), nullable=False, unique=True)
    original_name = Column(String(255), nullable=True)

    mime_type = Column(String(128), nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    checksum = Column(String(128), nullable=True)

    description = Column(Text, nullable=True)

    uploaded_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    patient = relationship("Patient", back_populates="files")
    checklist_item = relationship("PatientChecklistItem", back_populates="files")
    uploaded_by = relationship("User", back_populates="uploaded_files")