from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import date, datetime

from src.schemas.common import ORMBase
from src.models.patient import PatientStatus
from src.core.validators import validate_snils

class PatientCreate(BaseModel):
    organization_id: Optional[int] = None

    fio: str = Field(min_length=2, max_length=255)
    birth_date: Optional[date] = None
    sex: Optional[str] = Field(default=None, max_length=16)

    snils: Optional[str] = Field(default=None, max_length=64)
    polis: Optional[str] = Field(default=None, max_length=64)
    passport: Optional[str] = Field(default=None, max_length=64)

    diagnosis_text: Optional[str] = Field(default=None, max_length=255)
    operation_type: Optional[str] = Field(default=None, max_length=128)

    fhir_id: Optional[str] = Field(default=None, max_length=128)
    fhir_resource_json: Optional[Dict[str, Any]] = None
    external_system_id: Optional[str] = Field(default=None, max_length=128)

    status: PatientStatus = PatientStatus.NEW

    @field_validator("snils")
    @classmethod
    def _snils(cls, v):
        if not v:
            return None
        return validate_snils(v)

class PatientUpdate(BaseModel):
    organization_id: Optional[int] = None

    fio: Optional[str] = Field(default=None, min_length=2, max_length=255)
    birth_date: Optional[date] = None
    sex: Optional[str] = Field(default=None, max_length=16)

    snils: Optional[str] = Field(default=None, max_length=64)
    polis: Optional[str] = Field(default=None, max_length=64)
    passport: Optional[str] = Field(default=None, max_length=64)

    status: Optional[PatientStatus] = None

    diagnosis_text: Optional[str] = Field(default=None, max_length=255)
    operation_type: Optional[str] = Field(default=None, max_length=128)

    fhir_id: Optional[str] = Field(default=None, max_length=128)
    fhir_resource_json: Optional[Dict[str, Any]] = None
    external_system_id: Optional[str] = Field(default=None, max_length=128)

    @field_validator("snils")
    @classmethod
    def _snils(cls, v):
        if not v:
            return None
        return validate_snils(v)

class PatientOut(ORMBase):
    id: int
    organization_id: Optional[int] = None

    fio: str
    birth_date: Optional[date] = None
    sex: Optional[str] = None

    snils: Optional[str] = None
    polis: Optional[str] = None
    passport: Optional[str] = None

    status: PatientStatus

    diagnosis_text: Optional[str] = None
    operation_type: Optional[str] = None

    fhir_id: Optional[str] = None
    fhir_resource_json: Optional[Dict[str, Any]] = None
    external_system_id: Optional[str] = None

    created_at: datetime
    updated_at: datetime