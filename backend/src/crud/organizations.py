from src.crud.base import CRUDBase
from src.models.organization import Organization
from src.schemas.organization import OrganizationCreate, OrganizationUpdate

org_crud = CRUDBase[Organization, OrganizationCreate, OrganizationUpdate](Organization)