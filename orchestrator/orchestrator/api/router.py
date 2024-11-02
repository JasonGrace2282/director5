from fastapi import APIRouter
from .vm.router import vm_router

main_router = APIRouter()

main_router.include_router(vm_router, prefix="/vm", tags=["vm"])

