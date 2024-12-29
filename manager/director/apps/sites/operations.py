import contextlib
import traceback
from collections.abc import Callable, Iterator
from typing import Any, overload

from .models import Action, Operation, Site

type ActionCallback = Callable[[Site], Iterator[str]]


class OperationWrapper:
    def __init__(self, operation: Operation) -> None:
        self.operation = operation
        self.site = operation.site
        self.actions: list[tuple[Action, ActionCallback]] = []

    @overload
    def register_action[C: ActionCallback](
        self,
        name: str,
        callback: None = None,
        *,
        user_recoverable: bool,
    ) -> Callable[[C], C]: ...

    @overload
    def register_action[C: ActionCallback](
        self,
        name: str,
        callback: C,
        *,
        user_recoverable: bool,
    ) -> C: ...

    def register_action[C: ActionCallback](
        self,
        name: str,
        callback: C | None = None,
        *,
        user_recoverable: bool,
    ) -> C | Callable[[C], C]:
        """Schedules an action on the operation.

        Args:
            name: The name of the action.
            callback: The function to call when the action is executed.
            user_recoverable: Whether the action is recoverable by the user.

        Returns:
            The callback if it was provided, or a decorator that takes a callback.
        """
        created = False

        def decorator(callback: C) -> C:
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
        return decorator(callback)

    def execute_operation(
        self,
        scope: dict[str, Any] | None = None,
        *,
        new_action_callback: Callable[[Action], object] | None = None,
    ) -> bool:
        """Executes the actions on the operation.

        Returns:
            Whether the operation was successful.
        """
        scope = scope or {}
        for action, callback in self.actions:
            try:
                action.start_action()
                if new_action_callback:
                    new_action_callback(action)

                self._run_action(action, callback, scope)
            except BaseException as e:  # noqa: BLE001
                e.add_note(f"Scope: {scope}")
                action.message += f"{traceback.format_exc()}\n"
                action.result = False
                action.save()
                return False
        return True

    def _run_action(self, action: Action, callback: ActionCallback, scope: dict[str, Any]) -> None:
        """Runs an action with the given callback.

        Args:
            action: The action to run.
            callback: The callback to run.
            scope: The scope to pass to the callback.
        """
        for message in callback(self.site, scope):
            assert isinstance(message, str), "Messages must be strings"
            action.message += f"{message}\n"
            action.save()
        action.result = True
        action.save()


@contextlib.contextmanager
def auto_run_operation_wrapper(
    operation_id: int, scope: dict[str, Any]
) -> Iterator[OperationWrapper]:
    """A context manager that runs an operation from start to finish.

    It does the following:

    #. Gets an :class:`.Operation` from the database (with .get(), so raises DoesNotExist if absent).
    #. Creates an :class:`OperationWrapper` around the :class:`.Operation`.
    #. Passes the :class:`OperationWrapper` to the with statement.
    #. Runs the :class:`OperationWrapper` with the given scope when the with statement has finished.
    #. Deletes the :class:`.Operation` if it was successful.
    """
    operation = Operation.objects.get(id=operation_id)
    wrapper = OperationWrapper(operation)

    yield wrapper

    send_operation_updated_message(operation.site)

    def action_started(_: Action) -> None:
        send_operation_updated_message(operation.site)

    result = wrapper.execute_operation(scope, new_action_callback=action_started)

    if result:
        operation.action_set.all().delete()
        operation.delete()

    send_operation_updated_message(operation.site)


def send_operation_updated_message(site: Site) -> None:
    pass


def send_site_updated_message(site: Site) -> None:
    pass
