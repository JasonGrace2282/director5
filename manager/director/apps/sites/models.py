from __future__ import annotations

from typing import Any, Self

from django.conf import settings
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

from ..users.models import User


class SiteQuerySet(models.QuerySet):
    def filter_visible(self, user: User) -> Self:
        """Only show the sites the user can access.

        .. seealso::

            Use :meth:`filter_editable` for filtering for sites the user can edit.
        """
        if user.is_superuser:
            return self
        return self.filter(users=user)

    def filter_editable(self, user: User) -> Self:
        """Only show the sites the user can edit.

        .. seealso::

            Use :meth:`filter_visible` for filtering for sites the user can see.
        """
        query = self.filter_visible(user)
        if not user.is_superuser:
            query = query.filter(availability__in=["enabled", "not-served"])
        return query


def _default_docker_image() -> DockerImage:
    os_ = DockerOS.objects.get_or_create(name="ubuntu")[0]
    return DockerImage.objects.get_or_create(
        name="ubuntu",
        tag="latest",
        language="",
        operating_system=os_,
    )[0]


class Site(models.Model):
    """A representation of the information for a specific website.

    Sites can either be static, which would be the case if they're serving
    html/css/js that doesn't change, or dynamic, which would be the case of a webserver
    of some kind (Django, NodeJS, Axum, etc).

    Depending on the purpose, the site will be deployed at different urls.

    At the application level, we validate that databases can *only* be added to dynamic sites.
    However, to prevent accidental loss of data, we don't delete the database after a change from
    dynamic -> static.
    """

    TYPES = (("S", "Static"), ("D", "Dynamic"))

    PURPOSES = (
        ("legacy", "Legacy"),
        ("user", "User"),
        ("project", "Project"),
        ("activity", "Activity"),
        ("other", "Other"),
    )

    AVAILABILITIES = [
        ("enabled", "Enabled (fully functional)"),
        ("not-served", "Not served publicly"),
        ("disabled", "Disabled (not served, only viewable/editable by admins)"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        # Don't replace these classes with "\w". That allows Unicode characters. We just want ASCII.
        validators=[
            MinLengthValidator(2),
            RegexValidator(
                regex=r"^[a-z0-9]+(-[a-z0-9]+)*$",
                message="Site names must consist of lowercase letters, numbers, and dashes. Dashes "
                "must go between two non-dash characters.",
            ),
        ],
    )

    description = models.TextField(blank=True)

    docker_image = models.OneToOneField("DockerImage", on_delete=models.SET(_default_docker_image))

    mode = models.CharField(max_length=1, choices=TYPES)

    purpose = models.CharField(
        max_length=10,
        choices=PURPOSES,
        help_text="What the site was created for.",
    )

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="site_set",
    )

    database = models.OneToOneField(
        "Database",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="site",
    )

    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITIES,
        default="enabled",
        help_text="Controls who can access the site",
    )

    objects = SiteQuerySet.as_manager()

    id: int

    def __str__(self):
        return self.name


class DatabaseHost(models.Model):
    """The different types of databases offered to users.

    Users should never be able to see or interact with this model directly,
    but rather through the :class:`Database` model.
    """

    # These should be capable of being put in a database URL
    # Hence "postgres", not "postgresql"
    DBMS_TYPES = [
        ("postgres", "PostgreSQL"),
        ("mysql", "MySQL"),
    ]

    # These parameters are passed to the containers to tell them how to connect to the database.
    hostname = models.CharField(max_length=255)
    port = models.PositiveIntegerField()

    dbms = models.CharField(max_length=16, choices=DBMS_TYPES)

    # These are used by the appservers to connect to and administer the database.
    # If either is unset, 'hostname' and 'port' are used, respectively. (Note that setting
    # admin_port=0 will also force a fallback on 'port'.)
    # If admin_hostname begins with a "/", it will be interpreted as a Unix socket path.
    admin_hostname = models.CharField(max_length=255, null=False, blank=True, default="")
    admin_port = models.PositiveIntegerField(null=True, blank=True, default=None)

    admin_username = models.CharField(max_length=255, null=False, blank=False)
    admin_password = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return f"{self.dbms}://{self.hostname}:{self.port}"


class Database(models.Model):
    """A database for a specific site."""

    host = models.ForeignKey(DatabaseHost, on_delete=models.CASCADE)
    password = models.CharField(max_length=255, null=False, blank=False)

    site: Site

    def __str__(self) -> str:
        return self.redacted_db_url

    @property
    def username(self) -> str:
        return f"site_{self.site.id}"

    @property
    def redacted_db_url(self) -> str:
        return f"{self.host.dbms}://{self.username}:***@{self.host.hostname}:{self.host.port}/{self.username}"


class DockerImage(models.Model):
    """The docker image of a specific site."""

    LANGUAGES = [
        ("", "No language"),
        ("python", "Python"),
        ("node", "Node.js"),
        ("php", "PHP"),
    ]

    name = models.CharField(max_length=255)
    tag = models.CharField(
        max_length=255,
        validators=[RegexValidator(r"^[a-zA-Z0-9]+(\/[a-zA-Z0-9]+)?:[a-zA-Z0-9._-]+$")],
        help_text="For parent images, this should always be a tag of the form 'alpine:3.20'.",
        unique=True,
    )

    logo = models.ImageField(upload_to="docker_image_logos", blank=True)
    description = models.TextField(blank=True)

    operating_system = models.ForeignKey(
        "DockerOS",
        on_delete=models.PROTECT,
        related_name="docker_image_set",
    )
    language = models.CharField(
        max_length=30,
        blank=True,
        choices=LANGUAGES,
        help_text="The programming language of the image. Do not include the version.",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The base image. Null for parent images.",
    )

    def __str__(self):
        return self.name


class DockerActionQuerySet(models.QuerySet):
    """Custom queryset for :class:`DockerAction`."""

    def filter_for_image(self, img: DockerImage) -> Self:
        """Filter actions that work on a specific operating system."""
        return self.filter(operating_systems=img.operating_system, language=img.language)


class DockerAction(models.Model):
    r"""An action that can be performed while setting up a Docker image.

    These should NOT have any syntax-errors in them, as they will be run as::

        RUN cmd one && \
            cmd two
    """

    name = models.CharField(max_length=255)
    command = models.TextField()

    operating_systems: models.ManyToManyField[DockerOS, Any] = models.ManyToManyField(
        "DockerOS",
        related_name="docker_action_set",
        help_text="The operating systems this action can be run on. Mostly used for filtering.",
    )

    objects = DockerActionQuerySet.as_manager()

    def __str__(self):
        return self.name


class DockerOS(models.Model):
    """The operating system of a Docker image.

    Used mainly for filtering image actions.
    """

    OPERATING_SYSTEMS = [
        ("ubuntu", "Ubuntu"),
        ("alpine", "Alpine"),
        ("debian", "Debian"),
    ]

    name = models.CharField(
        max_length=100,
        choices=OPERATING_SYSTEMS,
        help_text="The name of the OS, in all ascii lowercase.",
        unique=True,
    )

    class Meta:
        verbose_name = "Docker OS"
        verbose_name_plural = "Docker OS's"

    def __str__(self):
        return self.name


class Domain(models.Model):
    """Represents a custom (non-`sites.tjhsst.edu`) domain.

    `sites.tjhsst.edu` domains MUST be set up by creating a site with that name.

    Note: It must be ensured that *.tjhsst.edu domains can only be set up by Director admins.

    """

    STATUSES = [
        # Enabled (most domains)
        ("active", "Active"),
        # Disabled (respected in generation of configuration, but currently no provisions for
        # setting domains to inactive)
        ("inactive", "Inactive"),
        # This domain was removed from the Site it was added to. All records of it should be
        # removed.
        ("deleted", "Deleted"),
        # Reserved domains we don't want people to use for legal/policy reasons (these should always
        # have site=None)
        ("blocked", "Blocked"),
    ]

    # Should ONLY be None for deleted or blocked domains
    site = models.ForeignKey(Site, null=True, on_delete=models.PROTECT)

    domain = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r"^(?!(.*\.)?sites\.tjhsst\.edu$)"
                r"[a-z0-9]+(-[a-z0-9]+)*(\.[a-z0-9]+(-[a-z0-9]+)*)+$$",
                message="Invalid domain. (Note: You can only have one sites.tjhsst.edu domain, and "
                "it must match the name of your site.)",
            )
        ],
    )

    created_time = models.DateTimeField(auto_now_add=True, null=False)
    creating_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    status = models.CharField(max_length=8, choices=STATUSES, default="active")

    def __str__(self) -> str:
        return f"{self.domain} ({self.site})"
