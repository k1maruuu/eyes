from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.schemas.common import ORMBase

class OpIn(BaseModel):
    op_id: str = Field(min_length=1, max_length=64)
    action: str = Field(min_length=1, max_length=64)
    payload: Dict[str, Any]
    created_at: Optional[int] = None  # epoch ms (PWA)

class BatchIn(BaseModel):
    ops: List[OpIn]

class OpResult(BaseModel):
    op_id: str
    status: str  # applied | duplicate | error
    message: Optional[str] = None

class BatchOut(BaseModel):
    results: List[OpResult]
    applied_ids: List[str]

class OperationLogOut(ORMBase):
    id: int
    op_id: str
    action: str
    payload: Dict[str, Any]
    user_id: Optional[int] = None
    created_at: datetime