from fastapi import APIRouter

from .docker.router import router as docker_router

main_router = APIRouter()
main_router.include_router(docker_router, prefix="/docker", tags=["docker"])
