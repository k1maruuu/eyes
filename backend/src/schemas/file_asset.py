from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .common import ORMBase

ReviewDecisionStr = str


class ReviewCreate(BaseModel):
    patient_id: int
    surgeon_user_id: Optional[int] = None
    decision: ReviewDecisionStr = Field(..., description="APPROVE | REQUEST_CHANGES")
    comment: Optional[str] = None


class ReviewOut(ORMBase):
    id: int
    patient_id: int
    surgeon_user_id: Optional[int] = None
    decision: str
    comment: Optional[str] = None
    created_at: datetime


class CommentCreate(BaseModel):
    patient_id: int
    author_user_id: Optional[int] = None
    text: str = Field(min_length=1)


class CommentOut(ORMBase):
    id: int
    patient_id: int
    author_user_id: Optional[int] = None
    text: str
    created_at: datetime


class FileAssetOut(BaseModel):
    id: int
    patient_id: int
    checklist_item_id: Optional[int] = None
    original_name: str
    content_type: str
    size_bytes: int
    storage_path: str
    kind: Optional[str] = None

    class Config:
        from_attributes = True