import random

from ..appserver import Appserver
from . import framework


def test_ping_appserver() -> None:
    """A test for :class:`.MockAppserver`."""
    data = {"message": "pong-mocked-appserver"}
    with framework.mock({"path": "/ping", "data": data}):
        appserver = random.choice(Appserver.list_pingable())
        response = appserver.http_request(
            path="/ping",
            method="POST",
            data={"message": f"pong-{appserver.host}"},
        )
        assert response.status_code == 200
        assert response.json() == data
