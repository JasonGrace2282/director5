import traceback
from typing import Any

from fastapi.responses import JSONResponse


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
