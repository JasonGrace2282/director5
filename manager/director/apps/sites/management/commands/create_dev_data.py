import shutil
from typing import TypedDict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from ... import tasks
from ...models import Site


class SiteInfo(TypedDict):
    name: str
    description: str
    mode: str
    purpose: str


class DatabaseData(TypedDict):
    pass


class Command(BaseCommand):
    help = "Create sites for development"

    def handle(self, *args, **kwargs):
        admin, created = get_user_model().objects.get_or_create(
            username="admin",
            is_superuser=True,
        )
        if created:
            admin.set_password("jasongrace")
            self.stdout.write(
                self.style.SUCCESS("Admin user created, with password 'jasongrace'!\n")
            )

        self.stdout.write("Creating python site...")

        try:
            self.create_site(
                {
                    "name": "python",
                    "description": "Python site",
                    "mode": "dynamic",
                    "purpose": "project",
                }
            )
        except Exception as e:
            raise CommandError(f"Failed to create python site: {e}") from e
        self.stdout.write(self.style.SUCCESS("Python site created!\n"))

    def create_site(self, create_data: SiteInfo, db_info: DatabaseData | None = None) -> None:
        if Site.objects.filter(name=create_data["name"]).exists():
            self.stdout.write(
                self.style.WARNING(f"Site {create_data['name']} already exists, skipping...")
            )
            return

        site = Site.objects.get(name=create_data["name"])
        create_op = site.start_operation("create_site")

        tasks.create_site.apply(create_op.id, throw=True)

        dst = (
            settings.BASE_DIR
            / "docker"
            / "storage"
            / "sites"
            / f"{site.id // 100:02d}"
            / f"{site.id % 100:02d}"
        )
        src = settings.BASE_DIR / "dev" / "sites" / create_data["name"]
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)

        docker_build_op = site.start_operation("update_docker_image")
        tasks.rebuild_docker_image.apply(docker_build_op.id, throw=True)

        if db_info is not None:
            # TODO after implementing database stuff
            pass
