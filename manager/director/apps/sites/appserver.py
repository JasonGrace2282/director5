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
        return f"{type(self).__name__}({self.protocol}://{self._host})"

    @staticmethod
    def protocol() -> str:
        """Returns the protocol to use for connecting to the appserver."""
        return "https" if settings.DIRECTOR_APPSERVER_SSL else "http"

    @classmethod
    def from_pingable(cls) -> Self:
        """Returns a random appserver that can be accessed."""
        hosts = [host for host in settings.DIRECTOR_APPSERVER_HOSTS if cls._can_ping(host)]
        if not hosts:
            raise RuntimeError("No pingable app servers found")
        return cls(random.choice(hosts))

    @classmethod
    def _can_ping(cls, host: str) -> bool:
        """Attempts to ping a given host with a message.

        Returns:
            Whether or not the host is pingable and responded correctly.
        """
        try:
            response = requests.get(f"{cls.protocol()}://{host}/ping", {"message": f"pong-{host}"})
            return response.status_code == 200 and response.json().get("message") == f"pong-{host}"
        except Exception:  # noqa: BLE001
            return False
