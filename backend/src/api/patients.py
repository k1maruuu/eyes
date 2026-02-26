from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from src.crud.patients import patient_crud
from src.services.deps import get_current_user, require_roles
from src.models.patient import PatientStatus, Patient
from src.models.user import User

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