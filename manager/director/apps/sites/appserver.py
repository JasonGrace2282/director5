"""A module for connecting to the appservers."""

import random
from typing import Self

import requests
from django.conf import settings


class Appserver:
    """An abstraction over a server running the orchestrator.

    You can create an instance by using :meth:`find_pingable`.
    """

    def __init__(self, appserver: str) -> None:
        self._host = appserver

    def __str__(self) -> str:
        return f"{type(self).__name__}(http://{self._host})"

    @classmethod
    def find_pingable(cls) -> Self:
        """Returns a random appserver that can be accessed."""
        hosts = []
        for host in settings.DIRECTOR_APPSERVER_HOSTS:
            if cls._ping(host):
                hosts.append(host)
        if not hosts:
            raise RuntimeError("No pingable app servers found")

        return cls(random.choice(hosts))

    @staticmethod
    def _ping(host: str) -> bool:
        try:
            response = requests.get(f"http://{host}/ping", {"message": f"pong-{host}"})
            return response.status_code == 200 and response.json().get("message") == f"pong-{host}"
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError):
            return False
