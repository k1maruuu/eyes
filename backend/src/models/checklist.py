from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.db.base import Base


class ChecklistTemplate(Base):
    __tablename__ = "checklist_templates"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    operation_type = Column(String(128), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    items = relationship("ChecklistItemTemplate", back_populates="template", cascade="all,delete", passive_deletes=True)
    patient_checklists = relationship("PatientChecklist", back_populates="template")


class ChecklistItemTemplate(Base):
    __tablename__ = "checklist_item_templates"

    id = Column(Integer, primary_key=True, index=True)

    template_id = Column(Integer, ForeignKey("checklist_templates.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    order_index = Column(Integer, default=0, nullable=False)

    requires_file = Column(Boolean, default=False, nullable=False)
    requires_value = Column(Boolean, default=False, nullable=False)
    value_hint = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    template = relationship("ChecklistTemplate", back_populates="items")
    patient_items = relationship("PatientChecklistItem", back_populates="item_template")