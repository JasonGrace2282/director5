from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, cast

from django.contrib.auth.decorators import user_passes_test

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

    from .models import User


def map_user(
    test_func: Callable[[User], bool],
) -> Callable[[AbstractBaseUser | AnonymousUser], bool]:
    """Fix types of test functions for :meth:`.user_passes_test`, and return False if the user is anonymous."""

    def wrapper(user: AbstractBaseUser | AnonymousUser) -> bool:
        if user.is_anonymous:
            return False
        return test_func(cast("User", user))

    return wrapper


teacher_or_superuser_required = user_passes_test(map_user(lambda u: u.is_teacher or u.is_superuser))
