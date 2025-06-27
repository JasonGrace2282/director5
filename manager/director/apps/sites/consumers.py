"""Consumers and Websockets for site urls."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, override

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.urls import path

from .models import Operation, Site

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

        # Listen for events for this site
        await self.channel_layer.group_add(
            site.channels_group_name(),
            self.channel_name,
        )

        await self.accept()
        info = await self.gather_site_info(site)
        await self.send(text_data=f"<code id='site-info'>\n{json.dumps(info, indent=4)}</code>")

    @database_sync_to_async
    def gather_site_info(self, site: Site) -> dict[str, Any]:
        """Returns a dictionary with information about the site."""
        site.refresh_from_db()
        info = {
            "name": site.name,
            "url": site.sites_url,
            "description": site.description,
            "purpose": site.purpose,
            "mode": site.mode,
            "users": list(site.users.values_list("username", flat=True)),
            "is_being_served": site.is_served,
        }

        if site.database is not None:
            # TODO
            pass

        op = Operation.objects.filter(site=site).first()
        if op is not None:
            operation_info = {
                "type": op.ty,
                "created_time": op.created_time.isoformat(),
                "started_time": (
                    op.started_time.isoformat() if op.started_time is not None else None
                ),
                "actions": [],
            }
            for action in op.list_actions_in_order():
                operation_info["actions"].append(
                    {
                        "slug": action.slug,
                        "name": action.name,
                        "started_time": (
                            action.started_time.isoformat()
                            if action.started_time is not None
                            else None
                        ),
                        "result": action.result,
                        "user_message": action.user_message,
                    }
                )
                if self.scope["user"].is_superuser:
                    operation_info["actions"][-1]["message"] = action.message

            info["operation"] = operation_info

        return info

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
