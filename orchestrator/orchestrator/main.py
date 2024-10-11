from fastapi import FastAPI

from . import firecracker

app = FastAPI()


@app.get("/ping", tags=["status"])
async def root(message: str = "pong"):
    """Check if the orchestrator is running."""
    return {"message": message}


app.include_router(firecracker.router, tags=["firecracker"])
