from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.services.deps import require_roles, get_current_user
from src.models.user import User

from src.crud.patients import patient_crud
from src.crud.checklists import patient_checklist_crud, patient_checklist_item_crud
from src.schemas.iol_calc import IOLCalcIn, IOLCalcOut
from src.services.iol_service import calculate_iol

router = APIRouter()


def _ensure_patient_scope(user: User, patient):
    if user.role.value != "admin" and user.organization_id != patient.organization_id:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/patients/{patient_id}/iol/calculate", response_model=IOLCalcOut)
def iol_calculate(
    patient_id: int,
    data: IOLCalcIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher")),
):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    _ensure_patient_scope(user, patient)

    # если передали checklist_item_id — проверим принадлежность пациенту
    if data.checklist_item_id is not None:
        checklist = patient_checklist_crud.get_latest_for_patient(db, patient_id)
        if not checklist:
            raise HTTPException(404, "Checklist not found")
        item = patient_checklist_item_crud.get_for_checklist(db, checklist.id, data.checklist_item_id)
        if not item:
            raise HTTPException(404, "Checklist item not found")

    calc = calculate_iol(db, patient_id, data)

    return IOLCalcOut(
        formula=calc.formula,
        result_d=calc.result_d,
        k1=calc.k1,
        k2=calc.k2,
        acd=calc.acd,
        axial_length=calc.axial_length,
        a_constant=calc.a_constant,
        saved_id=calc.id,
    )