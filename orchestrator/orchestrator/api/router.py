from fastapi import APIRouter

from .database.router import router as database_router
from .docker.router import router as docker_router
from .files.router import router as file_router

main_router = APIRouter()
main_router.include_router(docker_router, prefix="/docker", tags=["docker"])
main_router.include_router(file_router, prefix="/files", tags=["files"])
main_router.include_router(database_router, prefix="/database", tags=["database"])
