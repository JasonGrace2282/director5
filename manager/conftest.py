import pytest
from director.apps.sites.models import DockerAction, DockerImage
from django.utils.translation import activate


@pytest.fixture(autouse=True)
def set_default_language():
    activate("en")


@pytest.fixture(autouse=True)
def use_db_on_all_test(db):
    pass


@pytest.fixture(autouse=True)
def configure_settings(settings):
    # TODO: figure out why this is necessary
    settings.DEBUG = True


@pytest.fixture(autouse=True)
def new_media_root(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir


@pytest.fixture
def student(django_user_model):
    return django_user_model.objects.create_user(
        username="student",
        first_name="Ian",
        last_name="Fleming",
        password="password",
        is_student=True,
    )


@pytest.fixture
def teacher(django_user_model):
    return django_user_model.objects.create_user(
        username="teacher",
        first_name="Leigh",
        last_name="Bardugo",
        password="password",
        is_teacher=True,
    )


@pytest.fixture
def python_313():
    return DockerImage.objects.get_or_create(
        name="Python 3.13 (Alpine)",
        tag="python:3.13",
        language="python",
    )[0]


@pytest.fixture
def pip_install():
    return DockerAction.objects.get_or_create(
        name="pip-install",
        version=1,
        command="pip install -- {args}",
        allows_arguments=True,
    )[0]
