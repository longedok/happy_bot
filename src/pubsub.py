from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from client import Client

if TYPE_CHECKING:
    from redis import Redis


logger = logging.getLogger(__name__)


class RedisPubSub(threading.Thread):
    def __init__(self, client: Client, redis: Redis) -> None:
        super().__init__()

        self.client = client
        self.redis = redis

    def run(self) -> None:
        while True:
            key, message = self.redis.blpop("bot_messages")
            self.client.post_message(-641166626, message.decode("utf8"))
