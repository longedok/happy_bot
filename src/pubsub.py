from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aioredis import Redis

    from event_handler import EventHandler


logger = logging.getLogger(__name__)


class MessageType(Enum):
    BOT_ACCOUNT_LINKED = "bot_account_linked"


@dataclass
class Event:
    type: str
    payload: dict[str, Any]
    timestamp: float
    id: str = field(default=lambda: str(uuid.uuid4()))

    @classmethod
    def from_dict(cls, message_data) -> Event:
        return cls(
            id=message_data["id"],
            type=message_data["type"],
            timestamp=message_data["timestamp"],
            payload=message_data["payload"],
        )


class RedisPubSub:
    MESSAGES_LIST = "bot_messages"

    def __init__(self, event_handler: EventHandler, redis: Redis) -> None:
        self.event_handler = event_handler
        self.redis = redis

    async def run(self) -> None:
        while True:
            _, data = await self.redis.blpop(self.MESSAGES_LIST)
            event = self._parse_event(data)

            await self.event_handler.handle(event)

    @staticmethod
    def _parse_event(data: bytes) -> Event:
        parsed_data = json.loads(data.decode("utf8"))
        return Event.from_dict(parsed_data)
