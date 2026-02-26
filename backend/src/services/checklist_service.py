from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.crud.checklists import (
    template_crud,
    template_item_crud,
    patient_checklist_crud,
    patient_checklist_item_crud,
)
from src.models.patient import Patient, PatientStatus
from src.models.patient_checklist import PatientChecklist, PatientChecklistItem
from src.schemas.patient_checklist import (
    PatientChecklistCreate,
    PatientChecklistItemCreate,
    PatientChecklistItemUpdate,
)
from src.crud.checklists import patient_checklist_item_crud
from src.models.checklist import ChecklistItemTemplate
from src.models.file_asset import FileAsset


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_checklist_for_patient(
    db: Session,
    patient: Patient,
    template_id: Optional[int] = None,
) -> PatientChecklist:
    """
    Создаёт PatientChecklist + PatientChecklistItem[]:
    - если template_id передан -> используем его
    - иначе -> ищем активный шаблон по patient.operation_type
    """
    if template_id is not None:
        template = template_crud.get(db, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Checklist template not found")
        if not template.is_active:
            raise HTTPException(status_code=400, detail="Checklist template is not active")
    else:
        if not patient.operation_type:
            raise HTTPException(status_code=400, detail="Patient.operation_type is required to generate checklist")
        template = template_crud.get_active_for_operation(db, patient.operation_type)
        if not template:
            raise HTTPException(status_code=404, detail="No active checklist template for this operation_type")

    template_items = template_item_crud.list_for_template(db, template.id)
    if not template_items:
        raise HTTPException(status_code=400, detail="Template has no items")

    # 1) создаём шапку чеклиста
    checklist = patient_checklist_crud.create(
        db,
        PatientChecklistCreate(
            patient_id=patient.id,
            template_id=template.id,
            status="IN_PROGRESS",
        ),
    )

    # 2) создаём items по шаблону
    for it in template_items:
        patient_checklist_item_crud.create(
            db,
            PatientChecklistItemCreate(
                patient_checklist_id=checklist.id,
                item_template_id=it.id,
                done=False,
                value_text=None,
                note=None,
            ),
        )

    # 3) статус пациента: если только что создали план — логично перевести из NEW -> IN_PREPARATION
    if patient.status == PatientStatus.NEW:
        patient.status = PatientStatus.IN_PREPARATION
        db.add(patient)
        db.commit()
        db.refresh(patient)

    # подгружаем items (чтобы сразу вернуть с items)
    db.refresh(checklist)
    checklist.items  # trigger lazy-load при необходимости
    return checklist


def _recompute_patient_status_from_checklist(db: Session, patient: Patient, checklist: PatientChecklist) -> None:
    """
    MVP правило:
    - если все пункты done -> READY_FOR_REVIEW + checklist COMPLETED
    - иначе (если пациент был NEW) -> IN_PREPARATION
    Важно: статусы "после хирурга" не перетираем.
    """
    items = patient_checklist_item_crud.list_for_checklist(db, checklist.id)
    all_done = all(i.done for i in items) if items else False

    # если пациент уже в стадиях после проверки хирурга/операции — не трогаем
    if patient.status in {
        PatientStatus.REVISION_REQUIRED,
        PatientStatus.APPROVED,
        PatientStatus.SURGERY_SCHEDULED,
        PatientStatus.SURGERY_DONE,
    }:
        # но чеклист можно пометить completed, если всё done
        if all_done and checklist.status != "COMPLETED":
            checklist.status = "COMPLETED"
            db.add(checklist)
            db.commit()
        return

    if all_done:
        patient.status = PatientStatus.READY_FOR_REVIEW
        checklist.status = "COMPLETED"
    else:
        if patient.status == PatientStatus.NEW:
            patient.status = PatientStatus.IN_PREPARATION
        if checklist.status == "COMPLETED":
            checklist.status = "IN_PROGRESS"

    db.add(patient)
    db.add(checklist)
    db.commit()


def update_patient_checklist_item(
    db: Session,
    patient: Patient,
    checklist: PatientChecklist,
    item_id: int,
    patch: PatientChecklistItemUpdate,
) -> PatientChecklistItem:
    """
    Обновляем один пункт чек-листа и пересчитываем статус пациента.
    """
    item = patient_checklist_item_crud.get_for_checklist(db, checklist.id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    # done_at управляем аккуратно:
    data = patch.model_dump(exclude_unset=True)

    if "done" in data:
        if data["done"] is True and not item.done:
            data["done_at"] = _utcnow()
        if data["done"] is False:
            data["done_at"] = None

    tpl = db.query(ChecklistItemTemplate).filter(ChecklistItemTemplate.id == item.item_template_id).one_or_none()
    if not tpl:
        raise HTTPException(status_code=500, detail="Checklist item template missing")

    data = patch.model_dump(exclude_unset=True)

    # Если пытаемся поставить done=True — проверяем требования
    if data.get("done") is True:
        if tpl.requires_value and not (data.get("value_text") or item.value_text):
            raise HTTPException(status_code=400, detail="This item requires value_text before marking done")

        if tpl.requires_file:
            # ищем хотя бы один файл, привязанный к этому пункту
            has_file = (
                db.query(FileAsset)
                .filter(FileAsset.checklist_item_id == item.id)
                .first()
                is not None
            )
            if not has_file:
                raise HTTPException(status_code=400, detail="This item requires file upload before marking done")
            
        if getattr(tpl, "kind", None) == "BLOOD_LABS":
            panel = (
                db.query(BloodLabPanel)
                .filter(BloodLabPanel.patient_id == item.patient_id)
                .order_by(BloodLabPanel.id.desc())
                .first()
            )
            if not panel:
                raise HTTPException(status_code=400, detail="Blood labs are required before marking done")

            # минимальная мед-валидация (чтобы не вводили мусор)
            if panel.glucose_unit == "mmol/L" and not (0.5 <= panel.glucose_value <= 40):
                raise HTTPException(status_code=400, detail="Glucose value looks out of range")
            if panel.hemoglobin_unit == "g/L" and not (30 <= panel.hemoglobin_value <= 250):
                raise HTTPException(status_code=400, detail="Hemoglobin value looks out of range")

    updated = patient_checklist_item_crud.update(db, item, PatientChecklistItemUpdate(**data))

    # пересчитать статус пациента по прогрессу
    _recompute_patient_status_from_checklist(db, patient, checklist)

    return updated


def get_checklist_progress(db: Session, checklist: PatientChecklist) -> dict:
    items = patient_checklist_item_crud.list_for_checklist(db, checklist.id)
    total = len(items)
    done = sum(1 for i in items if i.done)
    percent = int(round((done / total) * 100)) if total > 0 else 0
    return {"done": done, "total": total, "percent": percent}