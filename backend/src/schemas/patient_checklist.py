from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from .common import ORMBase


class PatientChecklistCreate(BaseModel):
    patient_id: int
    template_id: Optional[int] = None
    status: str = Field(default="IN_PROGRESS", max_length=32)


class PatientChecklistUpdate(BaseModel):
    template_id: Optional[int] = None
    status: Optional[str] = Field(default=None, max_length=32)


class PatientChecklistOut(ORMBase):
    id: int
    patient_id: int
    template_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    items: List["PatientChecklistItemOut"] = []


class PatientChecklistItemCreate(BaseModel):
    patient_checklist_id: int
    item_template_id: int
    done: bool = False
    value_text: Optional[str] = None
    note: Optional[str] = None


class PatientChecklistItemUpdate(BaseModel):
    done: Optional[bool] = None
    value_text: Optional[str] = None
    note: Optional[str] = None
    done_at: Optional[datetime] = None


class PatientChecklistItemOut(ORMBase):
    id: int
    patient_checklist_id: int
    item_template_id: int

    done: bool
    done_at: Optional[datetime] = None
    value_text: Optional[str] = None
    note: Optional[str] = None

    created_at: datetime
    updated_at: datetime


PatientChecklistOut.model_rebuild()