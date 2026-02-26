from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from src.db.session import get_db
from src.services.deps import get_current_user, require_roles
from src.models.user import User
from src.models.checklist import ChecklistTemplate

router = APIRouter()

@router.get("/templates")
def list_templates(
    only_active: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    q = db.query(ChecklistTemplate).options(joinedload(ChecklistTemplate.items)).order_by(ChecklistTemplate.id.desc())
    if only_active:
        q = q.filter(ChecklistTemplate.is_active == True)  # noqa
    items=[]
    for t in q.all():
        items.append({
            "id": t.id,
            "title": t.title,
            "operation_type": t.operation_type,
            "version": t.version,
            "is_active": t.is_active,
            "items": [{
                "id": it.id,
                "title": it.title,
                "description": it.description,
                "order_index": it.order_index,
                "requires_file": it.requires_file,
                "requires_value": it.requires_value,
                "value_hint": it.value_hint,
            } for it in (t.items or [])]
        })
    return {"items": items}

@router.get("/templates/{template_id}")
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    t = db.query(ChecklistTemplate).options(joinedload(ChecklistTemplate.items)).filter(ChecklistTemplate.id==template_id).one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "id": t.id,
        "title": t.title,
        "operation_type": t.operation_type,
        "version": t.version,
        "is_active": t.is_active,
        "items": [{
            "id": it.id,
            "title": it.title,
            "description": it.description,
            "order_index": it.order_index,
            "requires_file": it.requires_file,
            "requires_value": it.requires_value,
            "value_hint": it.value_hint,
        } for it in (t.items or [])]
    }
