from typing import Any

from celery import shared_task

from . import actions
from .operations import auto_run_operation_wrapper


@shared_task
def create_site(operation_id: int) -> None:
    scope: dict[str, Any] = {}

    with auto_run_operation_wrapper(operation_id, scope) as wrapper:
        wrapper.register_action("Pinging appservers", actions.find_pingable_appservers)
        wrapper.register_action("Creating Docker service", actions.update_docker_service)
