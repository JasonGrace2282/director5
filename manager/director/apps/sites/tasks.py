from celery import shared_task


@shared_task
def create_site(site_id: int) -> None:
    pass
