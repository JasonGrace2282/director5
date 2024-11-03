"""Pydantic base models for validation."""

from ipaddress import IPv4Interface

from pydantic import BaseModel


class VMCreateRequest(BaseModel):
    name: str
    ip_interface: IPv4Interface
    site_id: int
    ram_mb: int
    vcpu_count: int
