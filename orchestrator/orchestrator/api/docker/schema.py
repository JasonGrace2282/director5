from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict, cast

from pydantic import (
    BaseModel,
    Field,
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


class ExceptionInfo(BaseModel):
    description: str
    explanation: str
    user_error: bool


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
    max_request_body_size: int


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

    @field_validator("url", mode="after")
    @classmethod
    def check_db_url(cls, v: PostgresDsn | MySQLDsn) -> PostgresDsn | MySQLDsn:
        if isinstance(v, PostgresDsn):
            assert len(v.hosts()) == 1, "Only one host is allowed"
            assert v.hosts()[0]["port"] is not None, "Port is required"
        return v

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.url}, {self.name})"


class DockerConfig(BaseModel):
    base: str
    """The base image for the container."""


# We're not too strict, the Manager should have a more
# conservative regex. We just want to double check to
# prevent injections into the Host traefik label.
DOMAIN_REGEX = r"^[a-zA-Z0-9][a-zA-Z0-9~.-]*[a-zA-Z0-9]$"


class SiteInfo(BaseModel):
    pk: int
    hosts: list[Annotated[str, Field(pattern=DOMAIN_REGEX)]]
    is_served: bool
    type_: Literal["static", "dynamic"]
    resource_limits: ResourceLimits
    docker: DockerConfig
    runfile: Annotated[str, Field(pattern=r"[/\-.a-zA-Z0-9]+")] | None = None
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

    def directory_path(self, *, on_host: bool = False) -> Path:
        """Returns the directory path on the local host where the site files are.

        Args:
            on_host: whether return it relative to ``SITES_DIR`` on the host machine.
                Should ONLY be used for the local development environment.
        """
        sites_dir = settings.HOST_SITES_DIR if on_host else settings.SITES_DIR
        # the specific path is a relic from Director4
        path = sites_dir / f"{self.pk // 100:02d}" / f"{self.pk % 100:02d}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def __str__(self) -> str:
        return f"site_{self.pk:04d}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.pk}, {self.is_served})"
