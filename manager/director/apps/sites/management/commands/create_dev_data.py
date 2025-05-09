import shutil
from typing import TypedDict

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from ...models import Site


class SiteInfo(TypedDict):
    name: str
    description: str
    mode: str
    purpose: str


class Command(BaseCommand):
    help = "Create sites for development"

    hostname = "127.0.0.1"
    port = "8080"

    def handle(self, *args, **kwargs):
        admin, created = get_user_model().objects.get_or_create(
            username="admin",
            is_superuser=True,
        )
        if created:
            admin.set_password("jasongrace")
            self.stdout.write(self.style.SUCCESS("Admin user created!\n"))
        self.stdout.write(
            f"Please navigate to http://{self.hostname}:{self.port} and login as admin, with the password jasongrace."
        )
        input("Press Enter to continue...")
        self.stdout.write("Creating python site...")

        self.create_site(
            {
                "name": "python",
                "description": "Python site",
                "mode": "dynamic",
                "purpose": "project",
            }
        )

    def create_site(self, create_data: SiteInfo) -> None:
        if Site.objects.filter(name=create_data["name"]).exists():
            self.stdout.write(
                self.style.WARNING(f"Site {create_data['name']} already exists, skipping...")
            )
            return
        try:
            response = requests.post(
                f"http://{self.hostname}:{self.port}{reverse('sites:create')}",
                json=create_data,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise CommandError(f"Error creating site: {e}") from e

        self.stdout.write(
            self.style.SUCCESS(
                f"Site {create_data['name']} created successfully! Updating contents..."
            )
        )
        site = Site.objects.get(name=create_data["name"])
        dst = (
            settings.BASE_DIR
            / "storage"
            / "sites"
            / f"{site.id // 100:02d}"
            / f"{site.id % 100:02d}"
        )
        src = settings.BASE_DIR / "dev" / "sites" / create_data["name"]
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
