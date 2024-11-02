from pydantic import BaseModel


class VMCreateRequest(BaseModel):
    name: str
    internal_ip: str
    ram_mb: int
    vcpu_count: float
    site_id: int