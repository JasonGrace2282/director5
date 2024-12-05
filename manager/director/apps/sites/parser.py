"""A module for parsing ``director.toml``."""

from dataclasses import dataclass
from typing import Any, TypedDict, cast

from .models import DockerAction, DockerImage, Domain

__all___ = ["parse_director_toml"]


class DockerActionData(TypedDict):
    action: DockerAction
    args: list[str]


@dataclass(slots=True)
class DockerConfig:
    base: DockerImage
    actions: list[DockerActionData]


@dataclass(slots=True)
class SiteConfig:
    docker: DockerConfig
    domain: list[Domain]


def parse_director_toml(data: dict[str, Any]) -> SiteConfig:
    """Parse and validate the ``director.toml``.

    Raises:
        KeyError: if a required key is missing.
        TypeError: if a key has an invalid type.
        ValueError: if a key has an invalid value.
    """
    project = data.get("project")
    if project is None:
        raise KeyError("Expected 'project' key in director.toml.")
    if not isinstance(project, dict):
        raise TypeError("Expected 'project' to be a dictionary.")

    version = project.get("version")
    if version is None:
        raise KeyError("Expected 'version' key in 'project'.")
    if not isinstance(version, int):
        raise ValueError("Expected 'version' to be an integer.")

    if version == 1:
        docker_data = data.get("docker")
        if docker_data is None:
            raise KeyError("Could not find 'docker` section.")
        docker = parse_docker_v1(docker_data)
    else:
        raise ValueError(f"Unknown version {version}")

    # TODO: parse domains
    return SiteConfig(docker=docker, domain=[])


def parse_docker_v1(data: dict[str, Any]) -> DockerConfig:
    """Parse and validate the ``[docker]`` section of the ``director.toml``.

    Assumes that ``[docker]`` exists, and the ``director.toml`` is in the v1 format.

    Raises:
        KeyError: if a required key is missing.
        TypeError: if a key has an invalid type.
        ValueError: if a key has an invalid value.
    """
    base_data = data.get("base")
    if base_data is None:
        raise KeyError("Expected 'base' key in [docker] section.")
    if not isinstance(base_data, str):
        raise TypeError("Expected 'base' to be a string.")
    base = cast(DockerImage, DockerImage.objects.filter(name__iexact=base_data).first())

    if base is None:
        raise ValueError(
            f"Could not find the base image `{base_data}`. Valid values:\n"
            f"{list(DockerImage.objects.values_list("name", flat=True))}"
        )

    actions: list[DockerActionData] = []
    for action_data in data.get("actions", []):
        if not isinstance(action_data, dict):
            raise TypeError("Expected 'actions' to be a list of dictionaries.")

        action = parse_action(action_data)
        actions.append(action)

    return DockerConfig(actions=actions, base=base)


def parse_action(action_data: dict[str, Any]) -> DockerActionData:
    """Parses an action in ``[[docker.actions]]``."""
    name = action_data.get("name")
    if name is None:
        raise KeyError("Expected 'name' key in 'actions'.")

    if not isinstance(name, str):
        raise TypeError("Expected 'name' to be a string.")

    name_data = name.strip().split("@")
    if len(name_data) != 2:
        raise ValueError("Expected 'name' to be in the format 'name@version'.")

    action_name, version = name_data
    version = version.removeprefix("v")

    action_query = DockerAction.objects.filter(name=action_name)
    if version != "latest":
        action = action_query.filter(version=version).first()
    else:
        action = action_query.order_by("version").last()

    if action is None:
        raise ValueError(
            f"Could not find the action `{action_name}` with version `{version}`. Valid values:\n"
            f"{[f"{name}@{version}" for name, version in DockerAction.objects.values_list("name", "version")]}"
        )

    args = action_data.get("args", [])
    if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
        raise TypeError(f"Expected 'args' for action {action.name} to be a list of strings.")

    return {"action": action, "args": args}
