from typing import Any, Protocol


class HasStdoutStderr(Protocol):
    @property
    def stdout(self) -> str: ...

    @property
    def stderr(self) -> str: ...


class FirecrackerError(Exception):
    type_: str = "firecracker"

    def __init__(
        self,
        process: HasStdoutStderr,
        msg: str = "",
    ) -> None:
        super().__init__(msg)
        self.process = process

    def to_dict(self) -> dict[str, Any]:
        return {
            "stdout": self.process.stdout,
            "stderr": self.process.stderr,
            "error_type": getattr(self, "type_", "No Description Provided"),
        }


class NetworkingError(FirecrackerError):
    """A networking-related error occurred during a firecracker task execution."""

    type_ = "networking"


class NoResourcesError(FirecrackerError):
    """Not enough resources were found to execute a given firecracker task."""

    type_ = "insufficient_resources"
