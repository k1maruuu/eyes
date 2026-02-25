from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class PatientChecklist(Base):
    __tablename__ = "patient_checklists"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("checklist_templates.id", ondelete="SET NULL"), nullable=True, index=True)

    status = Column(String(32), default="IN_PROGRESS", nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    patient = relationship("Patient", back_populates="checklists")
    template = relationship("ChecklistTemplate", back_populates="patient_checklists")
    items = relationship("PatientChecklistItem", back_populates="patient_checklist", cascade="all,delete", passive_deletes=True)


class PatientChecklistItem(Base):
    __tablename__ = "patient_checklist_items"
    __table_args__ = (
        UniqueConstraint("patient_checklist_id", "item_template_id", name="uq_patient_item_once"),
    )

    id = Column(Integer, primary_key=True, index=True)

    patient_checklist_id = Column(Integer, ForeignKey("patient_checklists.id", ondelete="CASCADE"), nullable=False, index=True)
    item_template_id = Column(Integer, ForeignKey("checklist_item_templates.id", ondelete="CASCADE"), nullable=False, index=True)

    done = Column(Boolean, default=False, nullable=False)
    done_at = Column(DateTime(timezone=True), nullable=True)

    # Универсальное значение (в MVP хватит)
    value_text = Column(Text, nullable=True)

    # Замечание по пункту
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    patient_checklist = relationship("PatientChecklist", back_populates="items")
    item_template = relationship("ChecklistItemTemplate", back_populates="patient_items")
    files = relationship("FileAsset", back_populates="checklist_item", cascade="all,delete", passive_deletes=True)