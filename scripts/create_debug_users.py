#!/usr/bin/env python3

import os
import sys
from getpass import getpass
from pathlib import Path
from typing import cast

import django
from django.contrib.auth import get_user_model

# fmt: off
user_data = [
    #[username, is_teacher, is_student, is_staff, is_superuser]
    ["student", False, True, False, False],
    ["teacher", True, False, False, False],
    ["admin", False, False, True, True],
]
# fmt: on


def add_users_to_database(password: str, *, verbose: bool = True) -> None:
    from director.apps.users.models import User

    for (
        username,
        is_teacher,
        is_student,
        is_staff,
        is_superuser,
    ) in user_data:
        old_user, created = get_user_model().objects.get_or_create(username=username)
        user = cast(User, old_user)

        if not created:
            if verbose:
                print(f"User {username} already exists, skipping...")
            continue

        if verbose:
            print(f"Creating user {username}...")

        name = username.capitalize()
        user.first_name = name
        user.last_name = name
        user.email = f"{username}@example.com"
        user.is_teacher = is_teacher
        user.is_student = is_student
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save()


def main():
    password = getpass("Enter password for all users: ")
    add_users_to_database(password, verbose=True)


if __name__ == "__main__":
    sys.path.insert(
        0,
        str(Path(__file__).parent.parent.joinpath("manager").resolve()),
    )
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "director.settings")
    django.setup()
    main()
