from typing import Annotated, Any, Literal, TypedDict, cast

from pydantic import (
    BaseModel,
    MySQLDsn,
    PostgresDsn,
    UrlConstraints,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
)
from pydantic.functional_validators import AfterValidator, WrapValidator

from orchestrator.core import settings

from .conversions import convert_memory_limit, cpu_to_nano_cpus


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


def convert_memory_limit_validator(
    v: object,
    handler: ValidatorFunctionWrapHandler,
    _info: ValidationInfo,
) -> int:
    """Pydantic validator for the memory limit."""
    if isinstance(v, int | str):
        return convert_memory_limit(v)
    return handler(v)


class ResourceLimits(BaseModel):
    cpus: Annotated[float, AfterValidator(cpu_to_nano_cpus)]
    memory: Annotated[int, WrapValidator(convert_memory_limit_validator)]


_db_url_validator = UrlConstraints(host_required=True, default_port=5432)


class DatabaseInfo(BaseModel):
    url: Annotated[PostgresDsn, _db_url_validator] | Annotated[MySQLDsn, _db_url_validator]
    name: str

    username: str
    password: str

    @property
    def type_(self) -> Literal["postgres", "mysql"]:
        return cast(Literal["postgres", "mysql"], self.url.scheme)

    @property
    def port(self) -> int:
        if isinstance(self.url, PostgresDsn):
            port = self.url.hosts()[0]["port"]
        else:
            port = self.url.port
        assert port is not None
        return port

    @property
    def host(self) -> str:
        host = self.url.host if isinstance(self.url, MySQLDsn) else self.url.hosts()[0]["host"]
        # UrlConstraints(host_required=True) was used
        assert host is not None
        return host

    @field_validator("url")
    @classmethod
    def check_db_url(cls, v: PostgresDsn | MySQLDsn | None) -> PostgresDsn | MySQLDsn | None:
        if v is None:
            return v
        if isinstance(v, PostgresDsn):
            assert len(v.hosts()) == 1, "Only one host is allowed"
            assert v.hosts()[0]["port"] is not None, "Port is required"
        return v

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.url}, {self.name})"


class SiteInfo(BaseModel):
    pk: int
    is_served: bool
    resource_limits: ResourceLimits
    runfile: str | None = None
    db: DatabaseInfo | None = None

    def container_env(self) -> dict[str, Any]:
        env: dict[str, Any] = {
            "TZ": settings.TIMEZONE,
        }
        if self.db is not None:
            env |= {
                "DATABASE_URL": str(self.db),
                "DIRECTOR_DATABASE_URL": str(self.db),
                "DIRECTOR_DATABASE_TYPE": self.db.type_,
                "DIRECTOR_DATABASE_HOST": self.db.host,
                "DIRECTOR_DATABASE_PORT": self.db.port,
                "DIRECTOR_DATABASE_NAME": self.db.name,
                "DIRECTOR_DATABASE_USERNAME": self.db.username,
                "DIRECTOR_DATABASE_PASSWORD": self.db.password,
            }
        return env
