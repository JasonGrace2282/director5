from fastapi import APIRouter

from .docker_images.router import router as docker_router

main_router = APIRouter()
main_router.include_router(docker_router, prefix="/docker", tags=["docker"])
