from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.models import OperationLog, Patient
from src.schemas.oplog import OpIn, OpResult
from src.models.patient import PatientStatus

SUPPORTED_ACTIONS = {
    "create_patient",
    "submit_for_review",
    "surgeon_approve",
    "surgeon_request_changes",
    # позже: update_checklist_item, attach_file и т.д.
}

def apply_op(db: Session, op: OpIn, user_id: int | None) -> OpResult:
    # 1) идемпотентность
    if db.query(OperationLog).filter(OperationLog.op_id == op.op_id).one_or_none():
        return OpResult(op_id=op.op_id, status="duplicate")

    if op.action not in SUPPORTED_ACTIONS:
        return OpResult(op_id=op.op_id, status="error", message="Unsupported action")

    try:
        payload = op.payload or {}

        # 2) применяем действие
        if op.action == "create_patient":
            fio = payload.get("fio") or "Без имени"
            p = Patient(fio=fio, status=PatientStatus.NEW)
            db.add(p)
            db.flush()

        else:
            pid = payload.get("patient_id")
            if not pid:
                raise ValueError("patient_id is required")
            p = db.get(Patient, int(pid))
            if not p:
                raise ValueError("patient not found")

            if op.action == "submit_for_review":
                p.status = PatientStatus.READY_FOR_REVIEW
            elif op.action == "surgeon_approve":
                p.status = PatientStatus.APPROVED
            elif op.action == "surgeon_request_changes":
                p.status = PatientStatus.REVISION_REQUIRED

            p.updated_at = datetime.now(timezone.utc)
            db.add(p)

        # 3) логируем операцию
        db.add(OperationLog(op_id=op.op_id, action=op.action, payload=op.payload, user_id=user_id))
        db.commit()
        return OpResult(op_id=op.op_id, status="applied")
    except Exception as e:
        db.rollback()
        return OpResult(op_id=op.op_id, status="error", message=str(e))