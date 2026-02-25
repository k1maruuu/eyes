from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.oplog import BatchIn, BatchOut
from src.services.deps import get_current_user, require_roles
from src.services.sync_service import apply_op

router = APIRouter()

@router.post("/batch", response_model=BatchOut)
def sync_batch(
    batch: BatchIn,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    results = []
    applied_ids = []
    for op in batch.ops:
        r = apply_op(db, op, user_id=user.id)
        results.append(r)
        if r.status == "applied":
            applied_ids.append(r.op_id)
    return BatchOut(results=results, applied_ids=applied_ids)