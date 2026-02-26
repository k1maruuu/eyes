from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.patient import PatientCreate, PatientUpdate, PatientOut, EmiassyncIn
from src.crud.patients import patient_crud
from src.services.deps import get_current_user, require_roles
from src.models.patient import PatientStatus, Patient
from src.models.user import User
from src.crud.checklists import patient_checklist_crud
from src.schemas.patient_checklist import (
    PatientChecklistOut,
    PatientChecklistItemOut,
    PatientChecklistItemUpdate,
    PatientChecklistProgressOut,
)
from src.services.checklist_service import (
    generate_checklist_for_patient,
    update_patient_checklist_item,
    get_checklist_progress,
)

from datetime import datetime

router = APIRouter()


def _ensure_patient_scope(user: User, patient: Patient) -> None:
    # admin видит всё
    if user.role.value == "admin":
        return
    # остальные — только свою организацию
    if patient.organization_id is None or user.organization_id is None:
        raise HTTPException(status_code=403, detail="Forbidden")
    if patient.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/", response_model=list[PatientOut])
def list_patients(
    status: PatientStatus | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    # Важно: фильтруем по organization_id, если не admin
    if user.role.value != "admin":
        return patient_crud.list_for_org(db, org_id=user.organization_id, status=status, limit=limit, offset=offset)

    return patient_crud.list(db, status=status, limit=limit, offset=offset)


@router.post("/", response_model=PatientOut)
def create_patient(
    data: PatientCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher")),
):
    # feldsher создаёт пациента только в своей org
    if user.role.value != "admin":
        data = data.model_copy(update={"organization_id": user.organization_id})
    return patient_crud.create(db, data)


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    obj = patient_crud.get(db, patient_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Patient not found")
    _ensure_patient_scope(user, obj)
    return obj


@router.patch("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    data: PatientUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    obj = patient_crud.get(db, patient_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Patient not found")
    _ensure_patient_scope(user, obj)

    # feldsher не должен менять org_id вручную
    if user.role.value != "admin":
        data = data.model_copy(update={"organization_id": obj.organization_id})

    return patient_crud.update(db, obj, data)


@router.post("/{patient_id}/emias-sync")
def emias_sync(patient_id: int, data: EmiassyncIn,
               db: Session = Depends(get_db),
               user=Depends(get_current_user)):
    patient = patient_crud.get(db, id=patient_id)
    _ensure_patient_scope(user, patient)

    # заглушка
    patient.fhir_id = f"mock-{patient_id}"
    patient.fhir_resource_json = {
        "resourceType": "Patient",
        "syncedAt": datetime.utcnow().isoformat(),
        "polis": data.polis,
        "snils": data.snils,
    }
    db.add(patient); db.commit(); db.refresh(patient)
    return {"ok": True, "fhir_id": patient.fhir_id}


# --- (B) Generate checklist for patient ---
@router.post("/{patient_id}/checklist/generate", response_model=PatientChecklistOut)
def generate_patient_checklist(
    patient_id: int,
    template_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher")),
):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    _ensure_patient_scope(user, patient)

    checklist = generate_checklist_for_patient(db, patient, template_id=template_id)
    # подгружаем items (если не подгрузились)
    checklist.items
    return checklist


# --- Get latest checklist for patient ---
@router.get("/{patient_id}/checklist", response_model=PatientChecklistOut)
def get_latest_patient_checklist(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    _ensure_patient_scope(user, patient)

    checklist = patient_checklist_crud.get_latest_for_patient(db, patient_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    checklist.items
    return checklist


# --- (C) Update checklist item ---
@router.patch("/{patient_id}/checklist/items/{item_id}", response_model=PatientChecklistItemOut)
def patch_patient_checklist_item(
    patient_id: int,
    item_id: int,
    data: PatientChecklistItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher")),
):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    _ensure_patient_scope(user, patient)

    checklist = patient_checklist_crud.get_latest_for_patient(db, patient_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")

    updated_item = update_patient_checklist_item(
        db=db,
        patient=patient,
        checklist=checklist,
        item_id=item_id,
        patch=data,
    )
    return updated_item


@router.get("/{patient_id}/checklist/progress", response_model=PatientChecklistProgressOut)
def get_patient_checklist_progress(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    _ensure_patient_scope(user, patient)

    checklist = patient_checklist_crud.get_latest_for_patient(db, patient_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")

    return get_checklist_progress(db, checklist)