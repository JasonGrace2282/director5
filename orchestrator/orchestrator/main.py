import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api.router import main_router

app = FastAPI(
    name="orchestrator",
    contact={"name": "Sysadmins", "email": "director@tjhsst.edu"},
)


@app.get("/ping", tags=["status"])
async def root(message: str = "pong"):
    """Check if the orchestrator is running."""
    return {"message": message}


app.include_router(main_router, prefix="/api")


@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    """Send traceback of exceptions to the Manager."""
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "user_error": False,
            "exception": traceback.format_exception(exc),
        },
    )
