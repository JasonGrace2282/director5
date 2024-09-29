from django.urls import reverse


def test_password_login(client, django_user_model):
    """Make sure logging in via password on the dev env works."""
    url = reverse("auth:password_login")

    django_user_model.objects.create_user("bob", password="password")

    response = client.post(url, {"username": "bob", "password": "password"})
    assert response.status_code == 302
