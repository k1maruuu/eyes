from fastapi import APIRouter
from src.api import auth, organizations, users, patients, sync, cases, dashboard, checklists

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(organizations.router, prefix="/orgs", tags=["organizations"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(checklists.router, prefix="/checklists", tags=["checklists"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
