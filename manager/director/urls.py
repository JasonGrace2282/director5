"""URL configuration for manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", include("director.apps.sites.urls", namespace="sites")),
    path("", include("director.apps.marketplace.urls", namespace="marketplace")),
    path("admin/", admin.site.urls),
    path("accounts/", include("director.apps.auth.urls", namespace="auth")),
    path("social-auth/", include("social_django.urls", namespace="social")),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
    urlpatterns += (
        path(
            "components.html",
            TemplateView.as_view(
                template_name="components.html",
                extra_context={"choices": [("d", "Django"), ("n", "Nodejs")]},
            ),
            name="components",
        ),
    )
    urlpatterns += debug_toolbar_urls()
