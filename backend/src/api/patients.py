from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from src.crud.patients import patient_crud
from src.services.deps import require_roles
from src.models.patient import PatientStatus

router = APIRouter()

@router.get("/", response_model=list[PatientOut])
def list_patients(
    status: PatientStatus | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    return patient_crud.list(db, status=status, limit=limit, offset=offset)

@router.post("/", response_model=PatientOut)
def create_patient(data: PatientCreate, db: Session = Depends(get_db), _=Depends(require_roles("admin", "feldsher"))):
    return patient_crud.create(db, data)

@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db), _=Depends(require_roles("admin", "feldsher", "surgeon"))):
    obj = patient_crud.get(db, patient_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Patient not found")
    return obj

@router.patch("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    data: PatientUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    obj = patient_crud.get(db, patient_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_crud.update(db, obj, data)