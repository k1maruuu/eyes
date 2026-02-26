from __future__ import annotations
from sqlalchemy.orm import Session
from src.models.blood_labs import BloodLabPanel

class CRUDBloodLabs:
    def create(self, db: Session, obj: BloodLabPanel) -> BloodLabPanel:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_latest_for_patient(self, db: Session, patient_id: int) -> BloodLabPanel | None:
        return (
            db.query(BloodLabPanel)
            .filter(BloodLabPanel.patient_id == patient_id)
            .order_by(BloodLabPanel.id.desc())
            .first()
        )

blood_labs_crud = CRUDBloodLabs()