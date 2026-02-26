from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.db.session import get_db
from src.services.deps import get_current_user, require_roles
from src.models.user import User
from src.models.patient import Patient
from src.models.patient_checklist import PatientChecklist

router = APIRouter()

@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    # counts for patients and cases
    patients_q = db.query(func.count(Patient.id))
    cases_q = db.query(PatientChecklist.status, func.count(PatientChecklist.id)).group_by(PatientChecklist.status)

    if user.role.value != "admin":
        patients_q = patients_q.filter(Patient.organization_id == user.organization_id)
        # join Patient for filtering cases by org
        cases_q = (
            db.query(PatientChecklist.status, func.count(PatientChecklist.id))
            .join(Patient, Patient.id == PatientChecklist.patient_id)
            .filter(Patient.organization_id == user.organization_id)
            .group_by(PatientChecklist.status)
        )

    total_patients = patients_q.scalar() or 0
    by_status = {s: c for s, c in cases_q.all()}

    return {
        "total_patients": total_patients,
        "cases_by_status": by_status,
    }
