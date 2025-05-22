import contextlib
import traceback
from collections.abc import Callable, Iterator
from functools import wraps
from typing import overload

from asgiref.sync import async_to_sync
from channels.layer import get_channel_layer

from .appserver import Appserver
from .models import Action, Operation, Site

type ActionCallback = Callable[[Site, list[Appserver]], Iterator[str]]
"""A callback that runs an action on a site.

Args:
    site: the :class:`.Site` to run the action on
    appservers: a list of pingable appservers
"""


class UserFacingError(Exception):
    """An exception used to signal that we failed with some helpful message.

    This should be used if the appserver has useful information on e.g. why
    a docker build failed. It will populate :attr:`.Action.user_message` with
    the content.
    """


class OperationWrapper:
    """A wrapper around an :class:`.Operation` for registering actions to execute.

    Given an instance, register a specific action with :meth:`register_action`.
    Then, execute the actions sequentially by running :meth:`execute_operation`.
    """

    def __init__(self, operation: Operation) -> None:
        self.operation = operation
        self.site = operation.site
        self.actions: list[tuple[Action, ActionCallback]] = []

    @overload
    def register_action(
        self,
        name: str,
        callback: None = None,
        *,
        user_recoverable: bool = ...,
    ) -> Callable[[ActionCallback], ActionCallback]: ...

    @overload
    def register_action(
        self,
        name: str,
        callback: ActionCallback,
        *,
        user_recoverable: bool = ...,
    ) -> ActionCallback: ...

    def register_action(
        self,
        name: str,
        callback: ActionCallback | None = None,
        *,
        user_recoverable: bool = False,
    ) -> ActionCallback | Callable[[ActionCallback], ActionCallback]:
        """Schedules an action on the operation.

        Can be used as a method, or as a decorator on a function.

        Args:
            name: The name of the action.
            callback: The function to call when the action is executed.
                It can yield messages to update the status of the action.
            user_recoverable: Whether the action is recoverable by the user.

        Returns:
            The callback if it was provided, or a decorator that takes a callback.
        """
        created = False

        def decorator(callback: ActionCallback) -> ActionCallback:
            nonlocal created
            assert not created, "Cannot decorate multiple actions"
            created = True

            action = Action.objects.create(
                operation=self.operation,
                slug=callback.__name__,
                name=name,
                user_recoverable=user_recoverable,
            )
            self.actions.append((action, callback))
            return callback

        if callback is None:
            return decorator
        decorator = wraps(callback)(decorator)
        return decorator(callback)

    def execute_operation(
        self, *, new_action_callback: Callable[[Action], object] | None = None
    ) -> bool:
        """Executes the actions on the operation.

        Returns:
            Whether the operation was successful.
        """
        appservers = Appserver.list_pingable()
        for action, callback in self.actions:
            try:
                action.start_action()
                if new_action_callback:
                    new_action_callback(action)

                self._run_action(action, callback, appservers)
            except UserFacingError as e:
                action.user_message += str(e)
                action.result = False
                action.save()
                return False
            except Exception:  # noqa: BLE001
                action.message += f"{traceback.format_exc()}\n"
                action.result = False
                action.save()
                return False
        return True

    def _run_action(
        self, action: Action, callback: ActionCallback, appservers: list[Appserver]
    ) -> None:
        """Runs an action with the given callback.

        Args:
            action: The action to run.
            callback: The callback to run.
            appservers: The pingable appservers
        """
        for message in callback(self.site, appservers):
            assert isinstance(message, str), "Messages must be strings"
            action.message += f"{message}\n"
            action.save()
        action.result = True
        action.save()


@contextlib.contextmanager
def auto_run_operation_wrapper(operation_id: int) -> Iterator[OperationWrapper]:
    """A context manager that runs an operation from start to finish.

    It does the following:

    #. Gets an :class:`.Operation` from the database (with ``.get()``, so raises ``DoesNotExist`` if absent).
    #. Creates an :class:`OperationWrapper` around the :class:`.Operation`.
    #. Passes the :class:`OperationWrapper` to the with statement.
    #. Runs the :class:`OperationWrapper` with the given scope when the with statement has finished.
    #. Deletes the :class:`.Operation` if it was successful.
    """
    operation = Operation.objects.select_related("site").get(id=operation_id)
    wrapper = OperationWrapper(operation)

    yield wrapper

    send_operation_updated_message(operation.site)

    def action_started(_: Action) -> None:
        send_operation_updated_message(operation.site)

    result = wrapper.execute_operation(new_action_callback=action_started)

    if result:
        operation.action_set.all().delete()
        operation.delete()

    send_operation_updated_message(operation.site)


@async_to_sync
async def send_operation_updated_message(site: Site) -> None:
    """Broadcast that the operation status has been updated."""
    await get_channel_layer().group_send(
        site.channels_group_name(),
        {"type": "operation.updated"},
    )


@async_to_sync
async def send_site_updated_message(site: Site) -> None:
    """Broadcast that the site metadata has been updated."""
    await get_channel_layer().group_send(
        site.channels_group_name(),
        {"type": "site.updated"},
    )
