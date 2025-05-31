"""Consumers and Websockets for site urls."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, override

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.urls import path

from .models import Site

if TYPE_CHECKING:
    from ..users.models import User


@database_sync_to_async
def find_site(site_id: int, user: User) -> Site:
    return Site.objects.filter_visible(user).get(id=site_id)


class SiteInfoConsumer(AsyncWebsocketConsumer):
    """This is the consumer for all generic site information."""

    @override
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return
        async with self.close_on_error():
            site_id = int(self.scope["url_route"]["kwargs"]["site_id"])
            site = await find_site(site_id, user)
        await self.channel_layer.group_add(
            site.channels_group_name(),
            self.channel_name,
        )

    @asynccontextmanager
    async def close_on_error(
        self, error: type[BaseException] | tuple[BaseException, ...] = Exception
    ) -> AsyncIterator[None]:
        try:
            yield
        except error:
            await self.close()


urlpatterns = [
    path("sites/<int:site_id>/", SiteInfoConsumer.as_asgi()),
]
