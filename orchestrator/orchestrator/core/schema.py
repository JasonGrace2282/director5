import subprocess
import traceback
from typing import Any, assert_never

import iptc
import pyroute2
import requests
from fastapi import status
from fastapi.responses import JSONResponse

from .exceptions import FirecrackerError


class APIResponse(JSONResponse):
    """A specialized :class:`fastapi.responses.JSONResponse`.

    ### Notes

    The success field is automatically set based on the status code.
    """

    def __init__(
        self,
        message: str | None = None,
        data: dict[str, str] | None = None,
        errors: dict[str, str] | None = None,
        status_code: int = 200,
        tb: BaseException | None = None,
    ):
        content: dict[str, Any] = {
            "success": 200 <= status_code <= 300,
            "message": message,
            "data": data,
            "errors": {"data": errors},
        }
        if tb:
            content["errors"]["traceback"] = traceback.format_exception(tb)
        super().__init__(content=content, status_code=status_code)


class APIError(APIResponse):
    """Probable user error occurred leading to a failure of a task."""

    def __init__(self, message: str):
        errors = {"stdout": "", "stderr": "", "type": "error"}
        super().__init__(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DetailedAPIError(APIResponse):
    """Probable user error occurred leading to a failure of a task.

    There is also more information available (such as a :class:`subprocess.CalledProcessError` or :class:`requests.HTTPError`)
    """

    def __init__(
        self,
        message: str,
        exception: subprocess.CalledProcessError
        | requests.HTTPError
        | pyroute2.NetlinkError
        | iptc.IPTCError,
    ):
        if isinstance(exception, subprocess.CalledProcessError):
            errors = FirecrackerError(exception).to_dict()
            errors["subprocess-args"] = exception.cmd
        elif isinstance(exception, requests.HTTPError):
            errors = {
                "stdout": exception.response.text,
                "stderr": f"{exception.response.reason} {exception.response.status_code} when sending to {exception.response.url} with headers {exception.response.headers}",
                "type": "requests",
            }
        elif isinstance(exception, pyroute2.NetlinkError):
            errors = {
                "stdout": "",
                "stderr": f"{exception.code}: {exception.args[1]}",
                "type": "pyroute2",
            }
        elif isinstance(exception, iptc.IPTCError):
            errors = {
                "stdout": "",
                "stderr": exception.args[0],
                "type": "python-iptables",
            }
        else:
            assert_never(exception)

        super().__init__(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            tb=exception,
        )
