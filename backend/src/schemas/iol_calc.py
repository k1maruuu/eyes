from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field

Formula = Literal["SRKT", "HAIGIS"]

class IOLCalcIn(BaseModel):
    formula: Formula = "SRKT"

    # biometry
    k1: float = Field(gt=30, lt=60)          # D
    k2: float = Field(gt=30, lt=60)          # D
    acd: float = Field(gt=1.0, lt=6.0)       # mm (preop ACD)
    axial_length: float = Field(gt=18.0, lt=35.0)  # mm

    # target refraction at spectacle plane (D), обычно 0
    target_refraction: float = 0.0

    # SRK/T
    a_constant: Optional[float] = Field(default=118.0, gt=100, lt=130)

    # Haigis constants
    haigis_a0: Optional[float] = None
    haigis_a1: float = 0.400
    haigis_a2: float = 0.100

    # если хочешь привязать расчёт к пункту чек-листа “Расчет ИОЛ”
    checklist_item_id: Optional[int] = None

class IOLCalcOut(BaseModel):
    formula: str
    result_d: float
    saved_id: int