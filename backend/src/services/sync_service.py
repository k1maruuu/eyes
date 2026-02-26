from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.models import OperationLog, Patient, User
from src.schemas.oplog import OpIn, OpResult
from src.models.patient import PatientStatus


SUPPORTED_ACTIONS = {
    "create_patient",
    "submit_for_review",
    "surgeon_approve",
    "surgeon_request_changes",
}

# какие роли могут делать какие действия
ACTION_ROLES = {
    "create_patient": {"admin", "feldsher"},
    "submit_for_review": {"admin", "feldsher"},
    "surgeon_approve": {"admin", "surgeon"},
    "surgeon_request_changes": {"admin", "surgeon"},
}


def _forbidden(op_id: str) -> OpResult:
    return OpResult(op_id=op_id, status="error", message="Forbidden")


def _bad_request(op_id: str, msg: str) -> OpResult:
    return OpResult(op_id=op_id, status="error", message=msg)


def _ensure_action_allowed(user: User, op: OpIn) -> bool:
    allowed = ACTION_ROLES.get(op.action)
    if not allowed:
        return False
    return user.role.value in allowed


def _ensure_patient_scope(user: User, patient: Patient) -> bool:
    # admin видит всё
    if user.role.value == "admin":
        return True
    if user.organization_id is None or patient.organization_id is None:
        return False
    return user.organization_id == patient.organization_id


def apply_op(db: Session, op: OpIn, user: User) -> OpResult:
    # 1) идемпотентность
    if db.query(OperationLog).filter(OperationLog.op_id == op.op_id).one_or_none():
        return OpResult(op_id=op.op_id, status="duplicate")

    if op.action not in SUPPORTED_ACTIONS:
        return _bad_request(op.op_id, "Unsupported action")

    # 2) проверка ролей на действие (RBAC)
    if not _ensure_action_allowed(user, op):
        return _forbidden(op.op_id)

    payload = op.payload or {}

    try:
        # 3) применяем действие
        if op.action == "create_patient":
            fio = payload.get("fio") or "Без имени"

            # org scope: если не admin, пациент создаётся в org пользователя
            org_id = payload.get("organization_id")
            if user.role.value != "admin":
                org_id = user.organization_id

            p = Patient(
                fio=fio,
                status=PatientStatus.NEW,
                organization_id=org_id,
            )
            db.add(p)
            db.flush()

        else:
            pid = payload.get("patient_id")
            if not pid:
                return _bad_request(op.op_id, "patient_id is required")

            p = db.get(Patient, int(pid))
            if not p:
                return _bad_request(op.op_id, "patient not found")

            # org scope check (закрывает IDOR)
            if not _ensure_patient_scope(user, p):
                return _forbidden(op.op_id)

            # state transitions
            if op.action == "submit_for_review":
                # пример: запретить отправку на ревью, если уже APPROVED
                if p.status in (PatientStatus.APPROVED, PatientStatus.SURGERY_DONE):
                    return _bad_request(op.op_id, "Invalid status transition")
                p.status = PatientStatus.READY_FOR_REVIEW

            elif op.action == "surgeon_approve":
                # логика: хирург может approve только если READY_FOR_REVIEW
                if p.status != PatientStatus.READY_FOR_REVIEW:
                    return _bad_request(op.op_id, "Invalid status transition")
                p.status = PatientStatus.APPROVED

            elif op.action == "surgeon_request_changes":
                if p.status != PatientStatus.READY_FOR_REVIEW:
                    return _bad_request(op.op_id, "Invalid status transition")
                p.status = PatientStatus.REVISION_REQUIRED

            p.updated_at = datetime.now(timezone.utc)
            db.add(p)

        # 4) логируем операцию (в payload можно оставить как есть)
        db.add(OperationLog(op_id=op.op_id, action=op.action, payload=payload, user_id=user.id))
        db.commit()
        return OpResult(op_id=op.op_id, status="applied")

    except Exception:
        db.rollback()
        # A10: не отдаём клиенту детали исключения
        return OpResult(op_id=op.op_id, status="error", message="Internal error")