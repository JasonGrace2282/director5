from django.conf import settings


def generic_info(_request) -> dict:
    return {
        "DOCS_URL": settings.DOCS_URL,
        "REPO_URL": settings.REPO_URL,
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
    }
