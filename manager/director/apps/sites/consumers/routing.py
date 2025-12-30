from django.urls import path

from director.apps.sites.consumers.site_status import SiteStatusConsumer

websocket_urlpatterns = [
    path("sites/<int:site_id>/websocket/status", SiteStatusConsumer.as_asgi()),
]
