from typing import TypedDict

from pydantic import BaseModel


class ContainerLimits(TypedDict, total=False):
    """The resource limits for building a container.

    Args:
        memory: the memory limit for building the container
        memswap: the memory+swap limit (or -1 to disable)
        cpu_shares: the CPU shares (relative weight)
        cpu_set_cpus: the CPUs in which to allow execution.
            Comma separated or hyphen-separated ranges.
    """

    memory: int
    memswap: int


class ContainerCreationInfo(TypedDict):
    build_stdout: list[str]


class ExceptionInfo(BaseModel):
    description: str
    traceback: str
