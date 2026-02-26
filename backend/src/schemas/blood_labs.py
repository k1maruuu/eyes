from __future__ import annotations
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

class BloodLabIn(BaseModel):
    glucose_value: float = Field(gt=0, lt=50)      # mmol/L разумный диапазон
    glucose_unit: str = "mmol/L"

    hemoglobin_value: float = Field(gt=0, lt=250)  # g/L разумный диапазон
    hemoglobin_unit: str = "g/L"

    taken_at: Optional[date] = None
    checklist_item_id: Optional[int] = None

class BloodLabOut(BaseModel):
    id: int
    patient_id: int
    checklist_item_id: Optional[int] = None

    glucose_value: float
    glucose_unit: str
    hemoglobin_value: float
    hemoglobin_unit: str

    taken_at: Optional[date] = None

    class Config:
        from_attributes = True