import subprocess
from typing import Literal


class FirecrackerError(Exception):
    _type: Literal["networking", "insufficient_resources"]

    def __init__(
        self, msg: str, process: subprocess.CompletedProcess[str] | subprocess.CalledProcessError
    ) -> None:
        super().__init__(msg)
        self.process = process

    def __str__(self) -> str:
        return f"{self.process.stderr} ({self._type})"

    def asdict(self) -> dict[str, str]:
        return {
            "stdout": self.process.stdout,
            "stderr": self.process.stderr,
            "error_type": self.type,
        }

    @property
    def type(self) -> str:
        try:
            return self._type
        except AttributeError:
            return "error"


class NetworkingError(FirecrackerError):
    """A networking-related error occurred during a firecracker task execution."""

    _type = "networking"


class NoResourcesError(FirecrackerError):
    """Not enough resources were found to execute a given firecracker task."""

    _type = "insufficient_resources"
