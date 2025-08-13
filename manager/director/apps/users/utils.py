from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, cast

from django.contrib.auth.decorators import user_passes_test
import pydenticon
from io import BytesIO
from django.core.files.base import ContentFile


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


def generate_avatar(username: str) -> ContentFile:
    foreground_colors = [
        "rgb(45,79,255)",  # blue
        "rgb(254,180,44)",  # orange
        "rgb(226,121,234)",  # pink
        "rgb(30,179,253)",  # cyan
        "rgb(232,77,65)",  # red
        "rgb(49,203,115)",  # green
    ]

    grad_year = username[:4]
    try:
        foreground_color = foreground_colors[int(grad_year) % len(foreground_colors)]
    except ValueError:
        foreground_color = "rgb(141,69,170)"  # purple, fallback color

    generator = pydenticon.Generator(5, 5, foreground=[foreground_color], background="rgb(248,244,244)")
    image_data = generator.generate(username, 200, 200, padding=(20, 20, 20, 20), output_format="png")

    return ContentFile(image_data, name=f"{username}_avatar.png")
