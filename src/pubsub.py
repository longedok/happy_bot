from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from client import Client

if TYPE_CHECKING:
    from aioredis import Redis


logger = logging.getLogger(__name__)


class RedisPubSub:
    def __init__(self, client: Client, redis: Redis) -> None:
        super().__init__()

        self.client = client
        self.redis = redis

    async def run(self) -> None:
        while True:
            key, message = await self.redis.blpop("bot_messages")
            await self.client.post_message(-641166626, message.decode("utf8"))
