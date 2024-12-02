import tomllib

import pytest

from . import parser


def test_parse_valid_toml_v1(python_313, pip_install) -> None:
    toml = """
    [project]
    version = 1

    [docker]
    base = "Python 3.13 (Alpine)"

    [[docker.actions]]
    name = "pip-install@v1"
    args = ["django"]
    """
    data = tomllib.loads(toml)
    site_config = parser.parse_director_toml(data)
    assert site_config.domain == []
    docker = site_config.docker
    assert docker.base == python_313
    assert len(docker.actions) == 1
    action = docker.actions[0]
    assert action["action"] == pip_install
    assert action["args"] == ["django"]


def test_missing_keys():
    toml = """
    [project]

    [docker]
    base = "Python 3.13 (Alpine)"

    [[docker.actions]]
    name = "pip-install@v1"
    args = ["django"]
    """
    data = tomllib.loads(toml)
    with pytest.raises(KeyError, match=".*version.*"):
        parser.parse_director_toml(data)

    del data["project"]

    with pytest.raises(KeyError, match=".*project.*"):
        parser.parse_director_toml(data)

    # missing [docker]
    data["project"] = {"version": 1}
    del data["docker"]

    with pytest.raises(KeyError, match="Could not find .*docker.*"):
        parser.parse_director_toml(data)

    # missing docker.base
    data["docker"] = {}

    with pytest.raises(KeyError, match=".*base.*"):
        parser.parse_director_toml(data)


def test_invalid_keys(python_313, pip_install) -> None:
    toml = """
    [project]
    version = 1

    [docker]
    base = "Python 3.13"

    [[docker.actions]]
    name = "pip-install@v1"
    args = ["django"]
    """
    data = tomllib.loads(toml)

    with pytest.raises(ValueError, match="Could not find the base image.*"):
        parser.parse_director_toml(data)

    # invalid format for pip install
    data["docker"]["base"] = "Python 3.13 (Alpine)"
    data["docker"]["actions"][0]["name"] = "pip-install"  # missing version

    # should show the correct name format
    with pytest.raises(ValueError, match=".*name@version.*"):
        parser.parse_director_toml(data)

    # try invalid version name with @latest
    data["docker"]["actions"][0]["name"] = "abcdef@latest"

    with pytest.raises(ValueError, match="Could not find the action.*"):
        parser.parse_director_toml(data)
