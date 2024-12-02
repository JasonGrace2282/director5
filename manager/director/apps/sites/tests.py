import tomllib

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
