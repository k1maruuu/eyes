from fastapi import APIRouter
from src.api import auth, organizations, users, patients, sync, checklists, files, iol, blood_labs


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(organizations.router, prefix="/orgs", tags=["organizations"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(checklists.router, prefix="/checklists", tags=["checklists"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(files.router, tags=["files"])
api_router.include_router(iol.router, tags=["iol"])
api_router.include_router(blood_labs.router, tags=["labs"])
