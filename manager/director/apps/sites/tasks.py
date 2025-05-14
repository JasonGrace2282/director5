from celery import shared_task
from django.conf import settings

from . import actions
from .models import Site
from .operations import auto_run_operation_wrapper


@shared_task
def create_site(operation_id: int) -> None:
    with auto_run_operation_wrapper(operation_id) as wrapper:
        wrapper.register_action(
            "Building Docker image",
            actions.build_docker_image,
            user_recoverable=True,
        )
        wrapper.register_action("Creating Docker service", actions.update_docker_service)


@shared_task
def rebuild_docker_image(operation_id: int) -> None:
    with auto_run_operation_wrapper(operation_id) as wrapper:
        wrapper.register_action(
            "Building Docker image",
            actions.build_docker_image,
            user_recoverable=True,
        )
        wrapper.register_action("Restarting Docker service", actions.update_docker_service)


@shared_task
def delete_site(operation_id: int) -> None:
    site = Site.objects.get(operation__id=operation_id)

    with auto_run_operation_wrapper(operation_id) as wrapper:
        if settings.SITE_DELETION_REMOVE_FILES:
            wrapper.register_action("Deleting site files", actions.delete_site_files)
        if settings.SITE_DELETION_REMOVE_DATABASE:
            wrapper.register_action("Deleting site database", actions.delete_site_database)

        wrapper.register_action("Deleting Docker service", actions.remove_docker_service)
        wrapper.register_action("Deleting Docker image", actions.remove_docker_image)

    site.delete()
