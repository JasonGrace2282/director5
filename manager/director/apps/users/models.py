from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.utils import timezone

from director.apps.sites.models import Site
from director.apps.users.utils import generate_avatar


class UserManager(DjangoUserManager):
    pass


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "email", "is_teacher"]

    username = models.CharField(unique=True, max_length=32, null=False, blank=False)
    first_name = models.CharField(max_length=35, null=False, blank=False)
    last_name = models.CharField(max_length=70, null=False, blank=False)
    email = models.EmailField(max_length=50, null=False, blank=False)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    graduation_year = models.PositiveSmallIntegerField(null=True, default=None, blank=True)

    is_active = models.BooleanField(default=True, null=False)
    is_student = models.BooleanField(default=False, null=False)
    is_teacher = models.BooleanField(default=False, null=False)
    is_superuser = models.BooleanField(default=False, null=False)
    is_staff = models.BooleanField(default=False, null=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    accepted_guidelines = models.BooleanField(default=False, null=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_currently_banned(self) -> bool:
        return self.bans.filter(
            models.Q(end_time__isnull=True) | models.Q(end_time__gt=timezone.now())
        ).exists()

    def get_social_auth(self):
        return self.social_auth.get(provider="ion")

    def save(self, *args, **kwargs):
        created = self._state.adding

        super().save(*args, **kwargs)

        if created and not self.avatar:
            avatar_file = generate_avatar(self.username)
            self.avatar.save(avatar_file.name, avatar_file)

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return f"<User: {self.username} ({self.id})>"


class Ban(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bans")
    reason = models.TextField(blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)  # if null, ban is permanent

    @property
    def is_active(self) -> bool:
        return self.start_time <= timezone.now() <= self.end_time

class RecentSite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recent_sites")
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "site")
        ordering = ["-viewed_at"]
        indexes = [
            models.Index(fields=["user", "viewed_at"]),
        ]