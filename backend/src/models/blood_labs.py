from __future__ import annotations
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date, DateTime
from datetime import datetime, timezone
from src.db.base import Base

def _utcnow():
    return datetime.now(timezone.utc)

class BloodLabPanel(Base):
    __tablename__ = "blood_lab_panel"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    checklist_item_id = Column(Integer, ForeignKey("patient_checklist_items.id"), nullable=True, index=True)

    glucose_value = Column(Float, nullable=False)
    glucose_unit = Column(String(16), nullable=False, default="mmol/L")

    hemoglobin_value = Column(Float, nullable=False)
    hemoglobin_unit = Column(String(16), nullable=False, default="g/L")

    taken_at = Column(Date, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)