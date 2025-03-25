from typing import Any

from celery import shared_task
from django.conf import settings

from . import actions
from .operations import auto_run_operation_wrapper


@shared_task
def create_site(operation_id: int) -> None:
    scope: dict[str, Any] = {}

    with auto_run_operation_wrapper(operation_id, scope) as wrapper:
        wrapper.register_action("Pinging appservers", actions.find_pingable_appservers)
        wrapper.register_action(
            "Building Docker image",
            actions.build_docker_image,
            user_recoverable=True,
        )
        wrapper.register_action("Creating Docker service", actions.update_docker_service)


@shared_task
def delete_site(operation_id: int) -> None:
    scope: dict[str, Any] = {}

    with auto_run_operation_wrapper(operation_id, scope) as wrapper:
        wrapper.register_action("Pinging appservers", actions.find_pingable_appservers)

        if settings.SITE_DELETION_REMOVE_FILES:
            wrapper.register_action("Deleting site files", actions.delete_site_files)
        if settings.SITE_DELETION_REMOVE_DATABASE:
            wrapper.register_action("Deleting site database", actions.delete_site_database)

        wrapper.register_action("Deleting Docker service", actions.remove_docker_service)
        wrapper.register_action("Deleting Docker image", actions.remove_docker_image)
