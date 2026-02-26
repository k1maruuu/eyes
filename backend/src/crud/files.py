from __future__ import annotations
from typing import Optional, Sequence
from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.file_asset import FileAsset
from src.schemas.file_asset import FileAssetOut 

class CRUDFiles(CRUDBase):
    def list_for_patient(self, db: Session, patient_id: int) -> Sequence[FileAsset]:
        return db.query(FileAsset).filter(FileAsset.patient_id == patient_id).order_by(FileAsset.id.desc()).all()

    def list_for_checklist_item(self, db: Session, checklist_item_id: int) -> Sequence[FileAsset]:
        return db.query(FileAsset).filter(FileAsset.checklist_item_id == checklist_item_id).order_by(FileAsset.id.desc()).all()

file_crud = CRUDFiles(FileAsset)