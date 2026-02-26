from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from .common import ORMBase


# ---- Template ----
class ChecklistTemplateCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    operation_type: str = Field(min_length=1, max_length=128)
    version: int = Field(default=1, ge=1)
    is_active: bool = True


class ChecklistTemplateUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=255)
    operation_type: Optional[str] = Field(default=None, min_length=1, max_length=128)
    version: Optional[int] = Field(default=None, ge=1)
    is_active: Optional[bool] = None


class ChecklistTemplateOut(ORMBase):
    id: int
    title: str
    operation_type: str
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: List["ChecklistItemTemplateOut"] = []


# ---- Item Template ----
class ChecklistItemTemplateCreate(BaseModel):
    template_id: int
    title: str = Field(min_length=2, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

    order_index: int = 0

    requires_file: bool = False
    requires_value: bool = False
    value_hint: Optional[str] = Field(default=None, max_length=255)


class ChecklistItemTemplateUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    order_index: Optional[int] = None

    requires_file: Optional[bool] = None
    requires_value: Optional[bool] = None
    value_hint: Optional[str] = Field(default=None, max_length=255)


class ChecklistItemTemplateOut(ORMBase):
    id: int
    template_id: int
    title: str
    description: Optional[str] = None
    order_index: int
    requires_file: bool
    requires_value: bool
    value_hint: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# важно для ссылок в ChecklistTemplateOut.items
ChecklistTemplateOut.model_rebuild()