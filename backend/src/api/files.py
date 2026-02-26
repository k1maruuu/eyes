from __future__ import annotations

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.services.deps import require_roles, get_current_user
from src.models.user import User
from src.crud.patients import patient_crud
from src.crud.checklists import patient_checklist_crud
from src.crud.checklists import patient_checklist_item_crud
from src.crud.files import file_crud
from src.models.file_asset import FileAsset
from src.schemas.file_asset import FileAssetOut

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

router = APIRouter()


def _ensure_patient_scope(user: User, patient):
    # используй свою реализацию, если уже есть в patients.py
    if user.role.value != "admin" and user.organization_id != patient.organization_id:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/patients/{patient_id}/files", response_model=FileAssetOut)
async def upload_patient_file(
    patient_id: int,
    checklist_item_id: int | None = None,
    kind: str | None = None,
    uploaded_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher")),
):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    _ensure_patient_scope(user, patient)

    # если указан checklist_item_id — проверим что он принадлежит этому пациенту
    if checklist_item_id is not None:
        checklist = patient_checklist_crud.get_latest_for_patient(db, patient_id)
        if not checklist:
            raise HTTPException(404, "Checklist not found")
        item = patient_checklist_item_crud.get_for_checklist(db, checklist.id, checklist_item_id)
        if not item:
            raise HTTPException(404, "Checklist item not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(uploaded_file.filename or "")[1]
    safe_name = f"{uuid.uuid4().hex}{ext}"
    storage_path = os.path.join(UPLOAD_DIR, safe_name)

    content = await uploaded_file.read()
    with open(storage_path, "wb") as f:
        f.write(content)

    fa = FileAsset(
        patient_id=patient_id,
        checklist_item_id=checklist_item_id,
        kind=kind,
        original_name=uploaded_file.filename or safe_name,
        content_type=uploaded_file.content_type or "application/octet-stream",
        size_bytes=len(content),
        storage_path=storage_path,
    )
    db.add(fa)
    db.commit()
    db.refresh(fa)
    return fa


@router.get("/patients/{patient_id}/files", response_model=list[FileAssetOut])
def list_patient_files(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    _ensure_patient_scope(user, patient)

    return list(file_crud.list_for_patient(db, patient_id))


@router.get("/files/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    fa = db.query(FileAsset).filter(FileAsset.id == file_id).one_or_none()
    if not fa:
        raise HTTPException(404, "File not found")

    patient = patient_crud.get(db, fa.patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    _ensure_patient_scope(user, patient)

    if not os.path.exists(fa.storage_path):
        raise HTTPException(404, "File missing on disk")

    return FileResponse(
        path=fa.storage_path,
        media_type=fa.content_type,
        filename=fa.original_name,
    )