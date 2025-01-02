"""A module for Director-specific types."""

from __future__ import annotations

from pathlib import Path
from typing import NotRequired, TypedDict

__all__ = ["SSLSettings"]


class SSLSettings(TypedDict):
    cafile: Path
    """Used to verify server certificates."""

    client_cert: NotRequired[ClientCertificateSettings]


class ClientCertificateSettings(TypedDict):
    certfile: Path
    keyfile: Path

    password: NotRequired[str]
    """Only required if private key is encrypted."""
