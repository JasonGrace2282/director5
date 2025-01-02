from getpass import getpass
from typing import cast

from director.apps.users.models import User
from django.core.management.base import BaseCommand

# fmt: off
user_data = [
    #[username, is_teacher, is_student, is_staff, is_superuser]
    ["student", False, True, False, False],
    ["teacher", True, False, False, False],
    ["admin", False, False, True, True],
]
# fmt: on


class Command(BaseCommand):
    help = "Create users for debugging"

    def add_arguments(self, parser):
        parser.add_argument("--noinput", action="store_true", help="Do not ask for password")
        parser.add_argument("--force", action="store_true", help="Force creation of users")

    def handle(self, *args, **options):
        if not options["noinput"]:
            pwd = getpass("Enter password for all users: ")
        else:
            pwd = "jasongrace"

        verbose = options["verbosity"] > 0

        for (
            username,
            is_teacher,
            is_student,
            is_staff,
            is_superuser,
        ) in user_data:
            old_user, created = User.objects.get_or_create(username=username)
            user = cast(User, old_user)

            if not created and not options["force"]:
                if verbose:
                    self.stdout.write(
                        self.style.WARNING(f"User {username} already exists, skipping...")
                    )
                continue

            name = username.capitalize()
            user.first_name = name
            user.last_name = name
            user.email = f"{username}@example.com"
            user.is_teacher = is_teacher
            user.is_student = is_student
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.set_password(pwd)
            user.save()

            if verbose:
                self.stdout.write(self.style.SUCCESS(f"Created user {username}..."))
