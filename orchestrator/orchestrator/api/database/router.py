from fastapi import APIRouter

from ..docker.schema import SiteInfo

router = APIRouter()


@router.post("/delete")
def delete_database(site: SiteInfo):
    # TODO!!!
    return {}
