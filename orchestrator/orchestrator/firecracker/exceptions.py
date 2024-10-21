import subprocess
from typing import Literal

__all__ = ["FirecrackerError", "IpError", "MachineError"]


class FirecrackerError(Exception):
    _type: Literal["ip", "machine-config"]

    def __init__(self, msg: str, process: subprocess.CompletedProcess[bytes]) -> None:
        super().__init__(msg)
        self.process = process

    @property
    def stdout(self) -> str:
        return self.process.stdout.decode("utf-8")

    @property
    def stderr(self) -> str:
        return self.process.stderr.decode("utf-8")

    def asdict(self) -> dict[str, str]:
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error_type": self._type,
        }


class IpError(FirecrackerError):
    _type = "ip"


class MachineError(FirecrackerError):
    _type = "machine-config"
