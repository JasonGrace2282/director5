import tomllib

import pytest
from pydantic import ValidationError

from .parser import SiteConfig


def test_parse_valid_toml_v1(python_313, pip_install) -> None:
    toml = """
    [project]
    domain = "example.com"

    [docker]
    base = "Python 3.13 (Alpine)"

    [[docker.actions]]
    name = "pip-install@v1"
    args = ["django"]
    """
    data = tomllib.loads(toml)
    config = SiteConfig.model_validate(data)
    assert config.project is not None
    assert config.project.domain == "example.com"
    assert config.docker is not None
    assert config.docker.base.name == "Python 3.13 (Alpine)"
    action_data = config.docker.actions[0]
    assert action_data.action.name == "pip-install"
    assert action_data.action.version == 1
    assert action_data.args == ["django"]


def test_missing_keys(python_313):
    toml = """
    [docker]
    base = "Python 3.13 (Alpine)"

    [[docker.actions]]
    name = "pip-install@v1"
    args = ["django"]
    """
    data = tomllib.loads(toml)

    # rename the action so it doesn't exist by this name
    python_313.name = "BOB"
    python_313.save()

    # no docker image with this name exists
    with pytest.raises(ValidationError):
        SiteConfig.model_validate(data)

    python_313.name = "Python 3.13 (Alpine)"
    python_313.save()

    # missing [docker]
    del data["docker"]
    with pytest.raises(ValidationError):
        SiteConfig.model_validate(data)

    # missing docker.base
    data["docker"] = {}

    with pytest.raises(ValidationError):
        SiteConfig.model_validate(data)


def test_invalid_keys(python_313, pip_install) -> None:
    toml = """
    [docker]
    base = "Python 3.13"

    [[docker.actions]]
    name = "pip-install@v1"
    args = ["django"]
    """
    data = tomllib.loads(toml)

    with pytest.raises(ValidationError):
        SiteConfig.model_validate(data)

    # invalid format for pip install
    data["docker"]["base"] = "Python 3.13 (Alpine)"
    data["docker"]["actions"][0]["name"] = "pip-install"  # missing version

    # should show the correct name format
    with pytest.raises(ValidationError):
        SiteConfig.model_validate(data)

    # try invalid version name with @latest
    data["docker"]["actions"][0]["name"] = "abcdef@latest"

    with pytest.raises(ValidationError):
        SiteConfig.model_validate(data)
