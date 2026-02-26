from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.crud.base import CRUDBase
from src.models.checklist import ChecklistTemplate, ChecklistItemTemplate
from src.models.patient_checklist import PatientChecklist, PatientChecklistItem
from src.schemas.checklist import (
    ChecklistTemplateCreate,
    ChecklistTemplateUpdate,
    ChecklistItemTemplateCreate,
    ChecklistItemTemplateUpdate,
)
from src.schemas.patient_checklist import (
    PatientChecklistCreate,
    PatientChecklistUpdate,
    PatientChecklistItemCreate,
    PatientChecklistItemUpdate,
)


class CRUDChecklistTemplate(CRUDBase[ChecklistTemplate, ChecklistTemplateCreate, ChecklistTemplateUpdate]):
    def list(
        self,
        db: Session,
        operation_type: Optional[str] = None,
        active_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[ChecklistTemplate]:
        q = db.query(ChecklistTemplate)
        if operation_type:
            q = q.filter(ChecklistTemplate.operation_type == operation_type)
        if active_only:
            q = q.filter(ChecklistTemplate.is_active.is_(True))
        return (
            q.order_by(desc(ChecklistTemplate.operation_type), desc(ChecklistTemplate.version))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_active_for_operation(self, db: Session, operation_type: str) -> Optional[ChecklistTemplate]:
        return (
            db.query(ChecklistTemplate)
            .filter(
                ChecklistTemplate.operation_type == operation_type,
                ChecklistTemplate.is_active.is_(True),
            )
            .order_by(desc(ChecklistTemplate.version))
            .first()
        )


class CRUDChecklistItemTemplate(CRUDBase[ChecklistItemTemplate, ChecklistItemTemplateCreate, ChecklistItemTemplateUpdate]):
    def list_for_template(self, db: Session, template_id: int) -> Sequence[ChecklistItemTemplate]:
        return (
            db.query(ChecklistItemTemplate)
            .filter(ChecklistItemTemplate.template_id == template_id)
            .order_by(ChecklistItemTemplate.order_index.asc(), ChecklistItemTemplate.id.asc())
            .all()
        )


class CRUDPatientChecklist(CRUDBase[PatientChecklist, PatientChecklistCreate, PatientChecklistUpdate]):
    def get_latest_for_patient(self, db: Session, patient_id: int) -> Optional[PatientChecklist]:
        return (
            db.query(PatientChecklist)
            .filter(PatientChecklist.patient_id == patient_id)
            .order_by(PatientChecklist.id.desc())
            .first()
        )


class CRUDPatientChecklistItem(CRUDBase[PatientChecklistItem, PatientChecklistItemCreate, PatientChecklistItemUpdate]):
    def list_for_checklist(self, db: Session, patient_checklist_id: int) -> Sequence[PatientChecklistItem]:
        return (
            db.query(PatientChecklistItem)
            .filter(PatientChecklistItem.patient_checklist_id == patient_checklist_id)
            .order_by(PatientChecklistItem.id.asc())
            .all()
        )

    def get_for_checklist(self, db: Session, patient_checklist_id: int, item_id: int) -> Optional[PatientChecklistItem]:
        return (
            db.query(PatientChecklistItem)
            .filter(
                PatientChecklistItem.patient_checklist_id == patient_checklist_id,
                PatientChecklistItem.id == item_id,
            )
            .one_or_none()
        )


template_crud = CRUDChecklistTemplate(ChecklistTemplate)
template_item_crud = CRUDChecklistItemTemplate(ChecklistItemTemplate)

patient_checklist_crud = CRUDPatientChecklist(PatientChecklist)
patient_checklist_item_crud = CRUDPatientChecklistItem(PatientChecklistItem)