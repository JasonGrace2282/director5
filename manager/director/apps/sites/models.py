from __future__ import annotations

import shlex
from typing import TYPE_CHECKING, Self

from django.conf import settings
from django.core.validators import MinLengthValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from ..users.models import User
    from .parser import SiteConfig


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
                message=(
                    "Site names must consist of lowercase letters, numbers, and dashes. "
                    "Dashes must go between two non-dash characters."
                ),
            ),
        ],
    )

    description = models.TextField(blank=True)

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

    @property
    def is_served(self) -> bool:
        return self.availability == "enabled"

    @property
    def sites_url(self) -> str:
        """Return the default URL where the site is served."""
        default = settings.SITE_URL_FORMATS[None]
        return settings.SITE_URL_FORMATS.get(self.purpose, default).format(self.name)

    def list_domains(self) -> list[str]:
        """Returns all the domains for a site."""
        return [
            ("https://" + domain) for domain in self.domain_set.values_list("domain", flat=True)
        ] + [self.sites_url]

    def docker_image(self, config: SiteConfig | None = None) -> str:
        """Return the Docker image for the site."""
        if self.mode == "S":
            return "nginx:latest"
        if config is not None and config.docker is not None:
            return config.docker.base
        return settings.DIRECTOR_DEFAULT_DOCKER_IMAGE

    def serialize_resource_limits(self) -> dict[str, float]:
        """Serialize the resource limits for the appservers."""
        # TODO: implement custom resource limits
        return {
            "cpus": settings.DIRECTOR_RESOURCES_DEFAULT_CPUS,
            "memory": settings.DIRECTOR_RESOURCES_DEFAULT_MEMORY_LIMIT,
            "max_request_body_size": settings.DIRECTOR_RESOURCES_MAX_REQUEST_BODY,
        }


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


class DockerAction(models.Model):
    """An action that can be performed while setting up a Docker image.

    Think of a Docker action as a single shell command in a
    docker ``RUN`` statement.

    Arguments to the command will by default be appended to the command::

        command = "pip install"
        subprocess.run(shlex.split(command) + args)

    The special marker ``{args}`` can be used in the command to specify
    where the arguments should be placed. This is roughly equivalent to::

        pre_args, post_args = split_by_marker(command, "{args}")
        escaped_args = [shlex.quote(arg) for arg in args]
        subprocess.run(pre_args + escaped_args + post_args)

    .. danger::

        :func:`shlex.quote` only handles escaping the shell. The command
        should still be wary of injection attacks. For example, just
        setting a command as ``pip install`` would allow users to do
        e.g. ``pip install --user django``. Instead, consider using::

            pip install --

        to prevent the user from passing arguments that are flags.
    """

    name = models.CharField(max_length=255)
    command = models.TextField()

    allows_arguments = models.BooleanField(
        default=False,
        help_text="Does the command expect arguments?",
    )

    version = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "version"],
                name="unique_action_version",
            )
        ]

    def __str__(self):
        return self.name

    def construct_command(self, args: list[str], *, shell: bool = False) -> list[str]:
        """Produces a command that can be passed to ``subprocess.run``.

        Args:
            args: the arguments to pass to the command.
            shell: whether to escape the command for the shell.

        .. warning::

            Do NOT call this command without checking if :attr:`allows_arguments`
            is ``True``, as it is a security vulnerability.
        """
        if not self.allows_arguments:
            raise ValueError(f"{self} does not allow arguments.")

        flag = "{args}"
        command = shlex.split(self.command)
        if flag not in command:
            return command
        if shell:
            args = [shlex.quote(arg) for arg in args]
        pre_args = command[: command.index(flag)]
        post_args = command[command.index(flag) + 1 :]
        return pre_args + args + post_args


class DockerImage(models.Model):
    """The parent docker images.

    This is the base image that will be used in
    the ``FROM`` tag in a ``Dockerfile``.
    """

    LANGUAGES = [
        ("", "No language"),
        ("python", "Python"),
        ("node", "Node.js"),
        ("php", "PHP"),
    ]

    name = models.CharField(
        max_length=255,
        unique=True,
    )
    tag = models.CharField(
        max_length=255,
        validators=[RegexValidator(r"^[a-zA-Z0-9]+(\/[a-zA-Z0-9]+)?:[a-zA-Z0-9._-]+$")],
        help_text="For parent images, this should always be a tag of the form 'alpine:3.20'.",
        unique=True,
    )

    logo = models.ImageField(upload_to="docker_image_logos", blank=True)
    description = models.TextField(blank=True)

    language = models.CharField(
        max_length=30,
        blank=True,
        choices=LANGUAGES,
        help_text="The programming language of the image. Do not include the version.",
    )

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


class Operation(models.Model):
    """A series of actions being performed on a site.

    Examples:
        * The initial site creation process
        * Renaming a site
        * Changing a site type

    .. note::

        All state for an :class:`Operation` is in the Celery task. The database entries are only for easier inspection
        of running/failed tasks, so restarting/continuing a failed Operation is not possible. Instead, one
        should try running the "Fix site" task, which does its best to ensure that the site is set up properly.
    """

    OPERATION_TYPES = [
        # Create a site (no database)
        ("create_site", "Creating site"),
        # Rename the site. Changes the site name and the default domain name.
        ("rename_site", "Renaming site"),
        # Change the site name and domain names
        ("edit_site_names", "Changing site name/domains"),
        # Change the site type (example: static -> dynamic)
        ("change_site_type", "Changing site type"),
        # Create a database for the site
        ("create_site_database", "Creating site database"),
        # Delete a database for the site
        ("delete_site_database", "Deleting site database"),
        # Regenerate the database password.
        ("regen_site_secrets", "Regenerating site secrets"),
        # Updating the site's resource limits
        ("update_resource_limits", "Updating site resource limits"),
        # Updating something about the site's Docker image
        ("update_docker_image", "Updating site Docker image"),
        # Delete a site, its files, its database, its Docker image, etc.
        ("delete_site", "Deleting site"),
        # Restart a site's swarm service
        ("restart_site", "Restarting site"),
        # Tries to ensure everything is correct. Builds the Docker image, and updates the Docker service.
        ("fix_site", "Attempting to fix site"),
    ]

    site = models.OneToOneField(Site, null=False, on_delete=models.PROTECT)
    ty = models.CharField(max_length=24, choices=OPERATION_TYPES, verbose_name="type")
    created_time = models.DateTimeField(auto_now_add=True, null=False)
    started_time = models.DateTimeField(null=True)

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.ty}"

    @property
    def has_started(self) -> bool:
        return self.started_time is not None


class Action(models.Model):
    """An individual task in an operation.

    A representation of the state of a single action in an operation. For
    example, if the operation is fixing docker, the actions might be

    * "rebuild_docker_image"
    * "restart_docker_service"
    """

    operation = models.ForeignKey(Operation, null=False, on_delete=models.PROTECT)

    # Example: "update_nginx_config"
    slug = models.CharField(
        max_length=40,
        null=False,
        blank=False,
        validators=[MinLengthValidator(4), RegexValidator(regex=r"^[a-z]+(_[a-z]+)+$")],
    )
    # May be displayed to the user for progress updates. Example: "Updating Nginx config"
    name = models.CharField(max_length=80, null=False, blank=False)
    # Time this action was started. Only None if it hasn't been started yet.
    started_time = models.DateTimeField(null=True)

    # None=Not finished, True=Successful, False=Failed
    result = models.BooleanField(null=True, default=None)

    message = models.TextField(
        null=False,
        blank=True,
        help_text=(
            "Message describing the actions taken (and/or what failed). "
            "Should always be set to allow for easier debugging.\n"
            "Only visible to superusers."
        ),
    )

    # Operations that fail because of failures in Actions with this field set to True will not
    # be exported in the Prometheus metrics, and they will have a special note on the operations
    # page.
    # The main practical use of this is for building the Docker image, which will fail if the user
    # enters an incorrect package name.
    user_recoverable = models.BooleanField(
        null=False, default=False, help_text="Can the user recover from this failure?"
    )

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.name}"

    def start_action(self) -> None:
        self.started_time = timezone.localtime()
        self.save(update_fields=["started_time"])
