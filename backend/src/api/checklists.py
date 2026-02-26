from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.services.deps import require_roles

from src.crud.checklists import template_crud, template_item_crud
from src.schemas.checklist import (
    ChecklistTemplateOut,
    ChecklistTemplateUpdate,
    ChecklistItemTemplateOut,
    ChecklistTemplateCreateWithItems,
    ChecklistItemTemplateCreate,
)

router = APIRouter()


@router.get("/templates", response_model=list[ChecklistTemplateOut])
def list_templates(
    operation_type: str | None = None,
    active_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    templates = template_crud.list(
        db,
        operation_type=operation_type,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )
    # Важно: ChecklistTemplateOut имеет items=[], но relationship items ленивый.
    # Для MVP можно просто вернуть как есть — фронт может отдельно запросить items.
    return list(templates)


@router.post("/templates", response_model=ChecklistTemplateOut)
def create_template_with_items(
    data: ChecklistTemplateCreateWithItems,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    if not data.items:
        raise HTTPException(status_code=400, detail="Template must contain at least 1 item")

    template = template_crud.create(
        db,
        obj_in=data.model_copy(update={"items": []}),  # create() не умеет items, поэтому создаём отдельно
    )

    # Добавляем пункты
    for item in data.items:
        template_item_crud.create(
            db,
            ChecklistItemTemplateCreate(
                template_id=template.id,
                title=item.title,
                description=item.description,
                order_index=item.order_index,
                requires_file=item.requires_file,
                requires_value=item.requires_value,
                value_hint=item.value_hint,
            ),
        )

    db.refresh(template)
    # Подтянем items чтобы вернуть их в ответе
    template.items
    return template


@router.get("/templates/{template_id}/items", response_model=list[ChecklistItemTemplateOut])
def list_template_items(
    template_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "feldsher", "surgeon")),
):
    template = template_crud.get(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Checklist template not found")
    return list(template_item_crud.list_for_template(db, template_id))


@router.patch("/templates/{template_id}", response_model=ChecklistTemplateOut)
def update_template(
    template_id: int,
    data: ChecklistTemplateUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    template = template_crud.get(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Checklist template not found")
    template = template_crud.update(db, template, data)
    template.items
    return template