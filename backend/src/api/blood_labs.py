from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.services.deps import require_roles, get_current_user
from src.models.user import User
from src.crud.patients import patient_crud
from src.crud.checklists import patient_checklist_crud, patient_checklist_item_crud
from src.crud.blood_labs import blood_labs_crud
from src.models.blood_labs import BloodLabPanel
from src.schemas.blood_labs import BloodLabIn, BloodLabOut

router = APIRouter()

def _ensure_patient_scope(user: User, patient):
    if user.role.value != "admin" and user.organization_id != patient.organization_id:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/patients/{patient_id}/labs/blood", response_model=BloodLabOut)
def save_blood_labs(
    patient_id: int,
    data: BloodLabIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher")),
):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    _ensure_patient_scope(user, patient)

    # если указали checklist_item_id — проверим, что принадлежит пациенту
    if data.checklist_item_id is not None:
        checklist = patient_checklist_crud.get_latest_for_patient(db, patient_id)
        if not checklist:
            raise HTTPException(404, "Checklist not found")
        item = patient_checklist_item_crud.get_for_checklist(db, checklist.id, data.checklist_item_id)
        if not item:
            raise HTTPException(404, "Checklist item not found")

    panel = BloodLabPanel(
        patient_id=patient_id,
        checklist_item_id=data.checklist_item_id,
        glucose_value=data.glucose_value,
        glucose_unit=data.glucose_unit,
        hemoglobin_value=data.hemoglobin_value,
        hemoglobin_unit=data.hemoglobin_unit,
        taken_at=data.taken_at,
    )
    return blood_labs_crud.create(db, panel)

@router.get("/patients/{patient_id}/labs/blood/latest", response_model=BloodLabOut)
def get_latest_blood_labs(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    _ensure_patient_scope(user, patient)

    panel = blood_labs_crud.get_latest_for_patient(db, patient_id)
    if not panel:
        raise HTTPException(404, "Blood labs not found")
    return panel