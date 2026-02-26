from __future__ import annotations
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from src.db.base import Base

def _utcnow():
    return datetime.now(timezone.utc)

class IOLCalculation(Base):
    __tablename__ = "iol_calculation"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    checklist_item_id = Column(Integer, ForeignKey("patient_checklist_items.id"), nullable=True, index=True)

    formula = Column(String(32), nullable=False)  # "SRK", "SRKT", "HAIGIS"
    k1 = Column(Float, nullable=False)
    k2 = Column(Float, nullable=False)
    acd = Column(Float, nullable=False)
    axial_length = Column(Float, nullable=False)
    a_constant = Column(Float, nullable=True)

    result_d = Column(Float, nullable=False)  # итоговая диоптрия
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    # optional relationships (если у тебя принято)
    patient = relationship("Patient", lazy="joined")