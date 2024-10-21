from pydantic import BaseModel
from pydantic.networks import IPvAnyAddress


class CreateInstanceOut(BaseModel):
    firecracker_ip: IPvAnyAddress
