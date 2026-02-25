from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from src.schemas.common import ORMBase

class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    city: Optional[str] = Field(default=None, max_length=128)
    region: Optional[str] = Field(default=None, max_length=128)
    address: Optional[str] = Field(default=None, max_length=255)

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    city: Optional[str] = Field(default=None, max_length=128)
    region: Optional[str] = Field(default=None, max_length=128)
    address: Optional[str] = Field(default=None, max_length=255)

class OrganizationOut(ORMBase):
    id: int
    name: str
    city: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime