"""A module for connecting to the appservers."""

from typing import Any, Self

import requests
from django.conf import settings


class Appserver:
    """An abstraction over a server running the orchestrator.

    Args:
        appservers: a list of the hostnames of (pingable) appservers

    Example::

        >>> import random
        >>> pingable = Appserver.list_pingable()
        >>> appserver = random.choice(pingable)
        >>> appserver.host in pingable
        True
    """

    def __init__(self, host: str) -> None:
        self.host = host

    @property
    def num(self) -> int:
        """Returns the index of the appserver in the list of appservers."""
        return settings.DIRECTOR_APPSERVER_HOSTS.index(self.host) + 1

    def __str__(self) -> str:
        return f"{type(self).__name__} {self.num}"

    @staticmethod
    def protocol() -> str:
        """Returns the protocol to use for connecting to the appserver."""
        return "https" if settings.DIRECTOR_APPSERVER_SSL else "http"

    @classmethod
    def list_pingable(cls) -> list[Self]:
        """Return a list of all pingable appservers."""
        hosts = [cls(host) for host in settings.DIRECTOR_APPSERVER_HOSTS if cls._can_ping(host)]
        if not hosts:
            raise RuntimeError("No pingable app servers found")
        return hosts

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

    def http_request(
        self, path: str, method: str, data: dict[str, Any] | None = None
    ) -> requests.Response:
        """Makes an HTTP request to the appserver.

        Args:
            path: the api endpoint
            method: the HTTP verb to use
            data: the json-deserializable data to send
        """
        assert path.startswith("/")
        try:
            response = requests.request(
                method.upper(), f"{self.protocol()}://{self.host}{path}", json=data
            )
        except (
            requests.ConnectionError,
            requests.ConnectTimeout,
            requests.HTTPError,
            requests.URLRequired,
            requests.TooManyRedirects,
            requests.ReadTimeout,
            requests.Timeout,
            requests.RequestException,
            requests.JSONDecodeError,
        ) as e:
            e.add_note(f"Failed to connect to {path} ({method=}) on {self}: {data=}")
            raise

        return response
