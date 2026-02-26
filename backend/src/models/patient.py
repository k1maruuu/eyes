from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as En

try:
    from sqlalchemy.dialects.postgresql import JSONB as JSONType
except Exception:
    from sqlalchemy import JSON as JSONType  # type: ignore

from src.db.base import Base

class PatientStatus(str, En):
    NEW = "NEW"
    IN_PREPARATION = "IN_PREPARATION"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    REVISION_REQUIRED = "REVISION_REQUIRED"
    APPROVED = "APPROVED"
    SURGERY_SCHEDULED = "SURGERY_SCHEDULED"
    SURGERY_DONE = "SURGERY_DONE"


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)

    fio = Column(String(255), nullable=False, index=True)
    birth_date = Column(Date, nullable=True)
    sex = Column(String(16), nullable=True)

    snils = Column(String(64), nullable=True, index=True)
    polis = Column(String(64), nullable=True, index=True)
    passport = Column(String(64), nullable=True)

    status = Column(Enum(PatientStatus), default=PatientStatus.NEW, nullable=False, index=True)

    diagnosis_text = Column(String(255), nullable=True)
    operation_type = Column(String(128), nullable=True, index=True)

    # HL7/FHIR compatibility stubs
    fhir_id = Column(String(128), nullable=True)
    fhir_resource_json = Column(JSONType, nullable=True)
    external_system_id = Column(String(128), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="patients")
    checklists = relationship("PatientChecklist", back_populates="patient", cascade="all,delete", passive_deletes=True)
    files = relationship("FileAsset", back_populates="patient", cascade="all,delete", passive_deletes=True)
    reviews = relationship("Review", back_populates="patient", cascade="all,delete", passive_deletes=True)
    comments = relationship("Comment", back_populates="patient", cascade="all,delete", passive_deletes=True)

    diagnosis_icd10 = Column(String(16), nullable=True, index=True)