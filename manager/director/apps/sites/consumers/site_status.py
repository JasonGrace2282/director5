import logging
from typing import Literal

from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.template.loader import render_to_string

from director.apps.sites.models import Site, Operation
from director.apps.users.models import User
from redis import asyncio as aioredis

from channels.generic.websocket import AsyncWebsocketConsumer
import json

from director.settings import REDIS_URL

logger = logging.getLogger(__name__)

_redis = None

async def _get_redis() -> aioredis.Redis:
    """
    Returns:
        An :class:`aioredis.Redis` instance, and avoids making a new connection if one already exists
        This helps save resources
    """
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(REDIS_URL)
    return _redis


class SiteStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.site_id = self.scope["url_route"]["kwargs"]["site_id"]
        self.group_name = f"site_{self.site_id}"
        self.redis = await _get_redis()

        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        try:
            if self.user.is_superuser:
                self.site = await Site.objects.aget(id=self.site_id)
            else:
                self.site = await Site.objects.aget(id=self.site_id, users=self.user)
        except Site.DoesNotExist:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Add this user to a redis set of active users
        await self.redis.sadd(self.group_name, self.user.id)
        # Let all connected user's know this user is now connected
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "send_active_users"}
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        # Remove this user from the redis set of active users
        await self.redis.srem(self.group_name, self.user.id)
        # Make sure other users know this user's connection is going away
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "send_active_users"}
        )

    async def send_power_event(self, event):
        power_event_template = render_to_string("base_with_site_header_and_nav.html.partials/status_indicator.html", {"site": self.site, "status": event["status"]})
        await self.send(text_data=power_event_template.strip())

    async def send_operation_updated_event(self, event):
        operation = await Operation.objects.filter(site=self.site).afirst()
        power_event_template = await sync_to_async(render_to_string)("site_dashboard.html.partials/operations_and_process_log.html", {"operation": operation})
        await self.send(text_data=power_event_template.strip())

    async def send_process_log_data_event(self, event):
        pass

    async def send_active_users(self, event):
        members = await self.redis.smembers(self.group_name)
        users = []
        for member_id in members:
            try:
                user = await User.objects.aget(id=member_id.decode("utf-8"))
                users.append(user)
            except User.DoesNotExist:
                logger.exception("Non critical error: a user does not exist when parsing the redis active users set"
                                 f"User id was {member_id}, group was {self.group_name}")

        active_users_template = render_to_string("base_with_site_header_and_nav.html.partials/active_users.html", {"active_users": users, "user": self.user})
        await self.send(text_data=active_users_template.strip())

def trigger_power_event(site: Site, status: Literal["Online", "Offline", "Restarting", "Starting", "Stopping"]):
    async_to_sync(get_channel_layer().group_send)(
        f"site_{site.id}",
        {
            "type": "send_power_event",
            "status": status,
        }
    )

def trigger_operation_updated_event(site: Site):
    async_to_sync(get_channel_layer().group_send)(
        f"site_{site.id}",
        {
            "type": "send_operation_updated_event",
        }
    )

def trigger_process_log_data_event(site: Site):
    async_to_sync(get_channel_layer().group_send)(
        f"site_{site.id}",
        {
            "type": "send_operation_updated_event",
        }
    )