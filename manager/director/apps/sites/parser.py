"""A module for parsing ``director.toml``."""

from collections.abc import Callable
from logging import getLogger
from pathlib import Path
from typing import Annotated, Any

from django.db import models
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from .models import DockerAction, DockerImage

__all___ = ["SiteConfig"]


logger = getLogger(__name__)


def filter_by[M: models.Model](cls: type[M], field: str) -> Callable[[Any], M]:
    """Validate a model by filtering by a field and calling ``get()``."""

    def wrapper(value: Any) -> M:
        try:
            return cls.objects.filter(**{field: value}).get()
        except cls.DoesNotExist as e:
            raise ValueError(f"Could not find {cls.__name__} with {field}={value!r}.") from e
        except cls.MultipleObjectsReturned:
            logger.error(
                f"Multiple {cls.__name__} objects found with {field}={value!r}.", exc_info=True
            )
            raise ValueError(
                "An internal error occurred - please contact a director admin"
            ) from None
        # let django figure out the typeerrors
        except TypeError:
            raise

    return wrapper


def filter_for_action(data: str) -> DockerAction:
    if len(data.split("@")) != 2:
        raise ValueError("Docker action must be in the format 'action@version'.")

    action, version = data.split("@")
    version = version.removeprefix("v")
    if version == "latest":
        docker_act = DockerAction.objects.filter(name=action).order_by("version").last()
    else:
        docker_act = DockerAction.objects.filter(name=action, version=version).first()

    if docker_act is None:
        raise ValueError(f"No docker action `{action}@{version}` found.")
    return docker_act


class ProjectConfig(BaseModel):
    domain: str | None = None
    runfile: Path | None = None


class DockerActionConfig(BaseModel):
    action: Annotated[
        DockerAction,
        BeforeValidator(filter_for_action, json_schema_input_type=str),
    ] = Field(validation_alias="name")

    args: list[str]

    # our validators convert django models to the right type
    model_config = ConfigDict(arbitrary_types_allowed=True)


class DockerConfig(BaseModel):
    base: Annotated[DockerImage, BeforeValidator(filter_by(DockerImage, "name"))]
    actions: list[DockerActionConfig]

    # our validators convert django models to the right type
    model_config = ConfigDict(arbitrary_types_allowed=True)


class SiteConfig(BaseModel):
    project: ProjectConfig | None = None
    docker: DockerConfig | None
