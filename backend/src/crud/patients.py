from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.patient import Patient
from src.schemas.patient import PatientCreate, PatientUpdate

class CRUDPatient(CRUDBase[Patient, PatientCreate, PatientUpdate]):
    def list(self, db: Session, status=None, limit: int = 50, offset: int = 0):
        q = db.query(Patient)
        if status is not None:
            q = q.filter(Patient.status == status)
        return q.order_by(Patient.updated_at.desc()).offset(offset).limit(limit).all()

patient_crud = CRUDPatient(Patient)