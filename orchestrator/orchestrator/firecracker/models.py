from pydantic import BaseModel
from pydantic.networks import IPvAnyAddress


class CreateInstanceOut(BaseModel):
    ip_address: IPvAnyAddress
