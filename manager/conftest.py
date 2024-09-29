import pytest
from django.utils.translation import activate


@pytest.fixture(autouse=True)
def set_default_language():
    activate("en")


@pytest.fixture(autouse=True)
def use_db_on_all_test(db):
    pass


@pytest.fixture(autouse=True)
def new_media_root(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir


def student(django_user_model):
    return django_user_model.objects.create_user(
        username="student",
        first_name="Ian",
        last_name="Fleming",
        password="password",
        is_student=True,
    )


def teacher(django_user_model):
    return django_user_model.objects.create_user(
        username="teacher",
        first_name="Leigh",
        last_name="Bardugo",
        password="password",
        is_teacher=True,
    )
