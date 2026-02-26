from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationOut
from src.crud.organizations import org_crud
from src.services.deps import require_roles

router = APIRouter()

@router.post("/", response_model=OrganizationOut)
def create_org(data: OrganizationCreate, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    return org_crud.create(db, data)

@router.get("/{org_id}", response_model=OrganizationOut)
def get_org(org_id: int, db: Session = Depends(get_db), _=Depends(require_roles("admin", "feldsher", "surgeon"))):
    obj = org_crud.get(db, org_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Organization not found")
    return obj

@router.patch("/{org_id}", response_model=OrganizationOut)
def update_org(org_id: int, data: OrganizationUpdate, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    obj = org_crud.get(db, org_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org_crud.update(db, obj, data)