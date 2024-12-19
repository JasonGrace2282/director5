import pytest
from fastapi.testclient import TestClient

from orchestrator.api.docker.schema import SiteInfo
from orchestrator.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def site_info() -> SiteInfo:
    return SiteInfo(
        pk=0,
        hosts=["example.localhost.com"],
        is_served=True,
        resource_limits={"cpus": 1, "memory": "1MiB"},
        docker={"base": "python:3.12-alpine"},
    )


@pytest.fixture
def db_site_info() -> SiteInfo:
    return SiteInfo(
        pk=0,
        hosts=["example.localhost.com"],
        is_served=True,
        resource_limits={"cpus": 1, "memory": "1MiB"},
        docker={"base": "python:3.12-alpine"},
        db={
            "url": "mysql://user:password@localhost:3306/db",
            "name": "db",
            "username": "user",
            "password": "password",
        },
    )
