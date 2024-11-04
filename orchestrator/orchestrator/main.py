import os
import sys

from fastapi import FastAPI, status
from starlette.requests import Request

from .api.router import main_router
from .core.exceptions import FirecrackerError
from .core.schema import APIResponse

if os.geteuid() != 0:
    sys.exit("Please run orchestrator with root privileges. Exiting.")

app = FastAPI(
    name="orchestrator",
    contact={"name": "Sysadmins", "email": "director@tjhsst.edu"},
)


@app.get("/ping", tags=["status"])
async def root(message: str = "pong"):
    """Check if the orchestrator is running."""
    return {"message": message}


@app.exception_handler(FirecrackerError)
async def firecracker_exception_handler(request: Request, exc: FirecrackerError) -> APIResponse:
    error_details = exc.to_dict()

    return APIResponse(
        message=f"A {exc.type_} error occurred. See the errors field for more info.",
        data=None,
        errors=error_details,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        tb=exc,
    )


app.include_router(main_router, prefix="/api", tags=["api"])
