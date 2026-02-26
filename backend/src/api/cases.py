from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from src.db.session import get_db
from src.services.deps import get_current_user, require_roles
from src.models.user import User
from src.models.patient_checklist import PatientChecklist, PatientChecklistItem
from src.models.checklist import ChecklistTemplate, ChecklistItemTemplate
from src.models.oplog import OperationLog
from src.models.review import Comment

router = APIRouter()

SYSTEM_OPERATION_TYPE = "SYSTEM"
MEAS_ITEM_TITLE = "MEASUREMENT_JSON"
CALC_ITEM_TITLE = "CALC_RESULT_JSON"

def _progress_percent(case: PatientChecklist) -> int:
    total = len(case.items or [])
    if total == 0:
        return 0
    done = sum(1 for i in case.items if i.done)
    return int(round((done / total) * 100))

def _ensure_system_templates(db: Session) -> tuple[ChecklistTemplate, ChecklistItemTemplate, ChecklistItemTemplate]:
    tpl = db.query(ChecklistTemplate).filter(ChecklistTemplate.operation_type == SYSTEM_OPERATION_TYPE).one_or_none()
    if not tpl:
        tpl = ChecklistTemplate(title="System", operation_type=SYSTEM_OPERATION_TYPE, version=1, is_active=True)
        db.add(tpl)
        db.commit()
        db.refresh(tpl)

    meas = (
        db.query(ChecklistItemTemplate)
        .filter(ChecklistItemTemplate.template_id == tpl.id, ChecklistItemTemplate.title == MEAS_ITEM_TITLE)
        .one_or_none()
    )
    if not meas:
        meas = ChecklistItemTemplate(
            template_id=tpl.id,
            title=MEAS_ITEM_TITLE,
            description="JSON measurements payload",
            order_index=0,
            requires_file=False,
            requires_value=True,
            value_hint="JSON",
        )
        db.add(meas)

    calc = (
        db.query(ChecklistItemTemplate)
        .filter(ChecklistItemTemplate.template_id == tpl.id, ChecklistItemTemplate.title == CALC_ITEM_TITLE)
        .one_or_none()
    )
    if not calc:
        calc = ChecklistItemTemplate(
            template_id=tpl.id,
            title=CALC_ITEM_TITLE,
            description="JSON calculation result",
            order_index=1,
            requires_file=False,
            requires_value=True,
            value_hint="JSON",
        )
        db.add(calc)

    db.commit()
    db.refresh(meas)
    db.refresh(calc)
    return tpl, meas, calc

def _log(db: Session, case_id: int, user: User, action: str, payload: dict[str, Any]) -> None:
    op_id = f"case:{case_id}:{datetime.now(timezone.utc).timestamp()}"
    rec = OperationLog(op_id=op_id, action=action, payload=payload, user_id=user.id)
    db.add(rec)
    db.commit()

@router.get("")
def list_cases(
    status: Optional[str] = None,
    patient_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    q = db.query(PatientChecklist).options(joinedload(PatientChecklist.items))
    if status:
        q = q.filter(PatientChecklist.status == status)
    if patient_id:
        q = q.filter(PatientChecklist.patient_id == patient_id)
    q = q.order_by(PatientChecklist.id.desc()).offset(offset).limit(limit)
    items = []
    for c in q.all():
        items.append({
            "id": c.id,
            "patient_id": c.patient_id,
            "template_id": c.template_id,
            "status": c.status,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "progress_percent": _progress_percent(c),
        })
    return {"items": items}

@router.get("/{case_id}")
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon", "patient")),
):
    case = (
        db.query(PatientChecklist)
        .options(joinedload(PatientChecklist.items).joinedload(PatientChecklistItem.item_template))
        .filter(PatientChecklist.id == case_id)
        .one_or_none()
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # history via operation_log filtered by op_id prefix
    history = (
        db.query(OperationLog)
        .filter(OperationLog.op_id.like(f"case:{case_id}:%"))
        .order_by(OperationLog.created_at.desc())
        .limit(200)
        .all()
    )
    hist_out = [{"action": h.action, "payload": h.payload, "user_id": h.user_id, "created_at": h.created_at} for h in history]

    # comments are patient-level in current schema
    comments = (
        db.query(Comment)
        .filter(Comment.patient_id == case.patient_id)
        .order_by(Comment.created_at.desc())
        .limit(200)
        .all()
    )
    comm_out = [{"id": c.id, "author_user_id": c.author_user_id, "text": c.text, "created_at": c.created_at} for c in comments]

    # map items with special kinds
    tpl, meas_tpl, calc_tpl = _ensure_system_templates(db)

    calc_result = None
    items_out = []
    for it in case.items:
        kind = "CHECKLIST_ITEM"
        v_json = None
        if it.item_template_id == meas_tpl.id:
            kind = "MEASUREMENT"
            try:
                v_json = json.loads(it.value_text or "{}")
            except Exception:
                v_json = {"raw": it.value_text}
        elif it.item_template_id == calc_tpl.id:
            kind = "CALC_RESULT"
            try:
                calc_result = json.loads(it.value_text or "{}")
                v_json = calc_result
            except Exception:
                calc_result = {"raw": it.value_text}
                v_json = calc_result

        items_out.append({
            "id": it.id,
            "item_template_id": it.item_template_id,
            "title": it.item_template.title if it.item_template else None,
            "done": it.done,
            "done_at": it.done_at,
            "value_text": it.value_text,
            "value_json": v_json,
            "note": it.note,
            "kind": kind,
        })

    return {
        "id": case.id,
        "patient_id": case.patient_id,
        "template_id": case.template_id,
        "status": case.status,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "progress_percent": _progress_percent(case),
        "items": items_out,
        "calc_result": calc_result,
        "history": hist_out,
        "comments": comm_out,
    }

@router.post("")
def create_case(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher")),
):
    patient_id = payload.get("patient_id")
    if not patient_id:
        raise HTTPException(status_code=422, detail="patient_id is required")
    template_id = payload.get("template_id")
    status = payload.get("status") or "DRAFT"
    case = PatientChecklist(patient_id=int(patient_id), template_id=template_id, status=status)
    db.add(case)
    db.commit()
    db.refresh(case)
    _log(db, case.id, user, "CASE_CREATED", {"patient_id": case.patient_id, "template_id": case.template_id, "status": case.status})
    return {"id": case.id}

@router.patch("/{case_id}")
def update_case(
    case_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    case = db.query(PatientChecklist).filter(PatientChecklist.id == case_id).one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    before = {"status": case.status, "template_id": case.template_id}
    if "status" in payload and payload["status"]:
        case.status = str(payload["status"])
    if "template_id" in payload:
        case.template_id = payload["template_id"]
    db.commit()
    _log(db, case_id, user, "CASE_UPDATED", {"before": before, "after": {"status": case.status, "template_id": case.template_id}})
    return {"ok": True}

@router.put("/{case_id}/measurements")
def put_measurements(
    case_id: int,
    meas: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    case = db.query(PatientChecklist).filter(PatientChecklist.id == case_id).one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    _, meas_tpl, _calc_tpl = _ensure_system_templates(db)

    item = (
        db.query(PatientChecklistItem)
        .filter(PatientChecklistItem.patient_checklist_id == case_id, PatientChecklistItem.item_template_id == meas_tpl.id)
        .one_or_none()
    )
    now = datetime.now(timezone.utc)
    if not item:
        item = PatientChecklistItem(
            patient_checklist_id=case_id,
            item_template_id=meas_tpl.id,
            done=True,
            done_at=now,
            value_text=json.dumps(meas, ensure_ascii=False),
        )
        db.add(item)
    else:
        item.value_text = json.dumps(meas, ensure_ascii=False)
        item.done = True
        item.done_at = now
    # move status forward if appropriate
    if case.status in ("NEED_DATA", "DRAFT", "IN_PROGRESS"):
        case.status = "ON_REVIEW"
    db.commit()
    _log(db, case_id, user, "MEASUREMENTS_UPSERT", {"measurements": meas})
    return {"ok": True}

@router.post("/{case_id}/calculate")
def calculate(
    case_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "surgeon")),
):
    case = db.query(PatientChecklist).filter(PatientChecklist.id == case_id).one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    _, meas_tpl, calc_tpl = _ensure_system_templates(db)
    meas_item = (
        db.query(PatientChecklistItem)
        .filter(PatientChecklistItem.patient_checklist_id == case_id, PatientChecklistItem.item_template_id == meas_tpl.id)
        .one_or_none()
    )
    meas = {}
    if meas_item and meas_item.value_text:
        try:
            meas = json.loads(meas_item.value_text)
        except Exception:
            meas = {}

    axial = meas.get("axial_length_mm")
    k1 = meas.get("k1_d")
    k2 = meas.get("k2_d")
    warnings = []
    if axial is None: warnings.append("axial_length_mm missing")
    if k1 is None: warnings.append("k1_d missing")
    if k2 is None: warnings.append("k2_d missing")

    result = {"recommended_iol_power": None, "warnings": warnings, "input": {"axial_length_mm": axial, "k1_d": k1, "k2_d": k2}}
    if axial is not None and k1 is not None and k2 is not None:
        try:
            kavg = (float(k1)+float(k2))/2.0
            # Simple deterministic formula (MVP)
            power = 118.0 - 2.5*float(axial) - 0.9*kavg
            result["recommended_iol_power"] = round(power, 2)
        except Exception as e:
            result["warnings"].append(f"calc error: {e}")

    now = datetime.now(timezone.utc)
    calc_item = (
        db.query(PatientChecklistItem)
        .filter(PatientChecklistItem.patient_checklist_id == case_id, PatientChecklistItem.item_template_id == calc_tpl.id)
        .one_or_none()
    )
    if not calc_item:
        calc_item = PatientChecklistItem(
            patient_checklist_id=case_id,
            item_template_id=calc_tpl.id,
            done=True,
            done_at=now,
            value_text=json.dumps(result, ensure_ascii=False),
        )
        db.add(calc_item)
    else:
        calc_item.value_text = json.dumps(result, ensure_ascii=False)
        calc_item.done = True
        calc_item.done_at = now

    # status update
    case.status = "CALCULATED"
    db.commit()
    _log(db, case_id, user, "CALCULATED", {"result": result})
    return {"ok": True, "result": result}

@router.get("/calc-queue/list")
def calc_queue_list(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "surgeon")),
):
    q = (
        db.query(PatientChecklist)
        .options(joinedload(PatientChecklist.items))
        .filter(PatientChecklist.status.in_(["IN_CALC_QUEUE", "ON_REVIEW", "CALCULATED"]))
        .order_by(PatientChecklist.id.desc())
        .offset(offset)
        .limit(limit)
    )
    items = [{"id": c.id, "patient_id": c.patient_id, "status": c.status, "progress_percent": _progress_percent(c)} for c in q.all()]
    return {"items": items}
