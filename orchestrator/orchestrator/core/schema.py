import subprocess

import requests
from pydantic import BaseModel
from starlette.responses import JSONResponse
from fastapi import status

from .exceptions import FirecrackerError


class APIResponse(JSONResponse):
    media_type = "application/json"

    def __init__(self, success: bool, message: str | None = None,
                 data: list[str] | None = None, errors: dict[str, str] | None = None,
                 status_code: int = 200):
        content = {
            "success": success,
            "message": message,
            "data": data,
            "errors": errors,
        }
        super().__init__(content=content, status_code=status_code)


class APIError(APIResponse):
    """Probable user error occurred leading to a failure of a task"""
    media_type = "application/json"

    def __init__(self, message: str):
        errors = {
            "stdout": "",
            "stderr": "",
            "type": "error"
        }
        super().__init__(success=False, message=message, errors=errors, status_code=status.HTTP_400_BAD_REQUEST)


class DetailedAPIError(APIResponse):
    """Probable user error occurred leading to a failure of a task, and you have a subprocess.CalledProcessError object or requests.models.Response to pass for more
    info"""
    media_type = "application/json"

    def __init__(self, message: str, exception: subprocess.CalledProcessError | requests.models.Response):
        if isinstance(exception, subprocess.CalledProcessError):
            errors = FirecrackerError("", exception).asdict()
            message = message + " " + str(exception.args)
        elif isinstance(exception, requests.models.Response):
            errors = {
                "stdout": exception.text,
                "stderr": f"{exception.reason} {exception.status_code} when sending to {exception.url} with {exception.headers}",
                "type": "requests"
            }
        else:
            raise TypeError

        super().__init__(success=False, message=message, errors=errors, status_code=status.HTTP_400_BAD_REQUEST)