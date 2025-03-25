import shutil

from fastapi import APIRouter

from ..docker.schema import SiteInfo

router = APIRouter()


@router.post("/delete-all")
def delete_all_site_files(site: SiteInfo):
    directory = site.directory_path()
    shutil.rmtree(directory, ignore_errors=True)
    return {}
