from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from telegram_client import TelegramClient

if TYPE_CHECKING:
    from aioredis import Redis


logger = logging.getLogger(__name__)


class MessageType(Enum):
    BOT_ACCOUNT_LINKED = "bot_account_linked"


@dataclass
class Message:
    type: str
    payload: dict[str, Any]
    timestamp: float
    id: str = field(default=lambda: str(uuid.uuid4()))

    @classmethod
    def from_dict(cls, message_data) -> Message:
        return cls(
            id=message_data["id"],
            type=message_data["type"],
            timestamp=message_data["timestamp"],
            payload=message_data["payload"],
        )


class RedisPubSub:
    MESSAGES_LIST = "bot_messages"

    def __init__(self, telegram_client: TelegramClient, redis: Redis) -> None:
        self.telegram_client = telegram_client
        self.redis = redis

    async def run(self) -> None:
        while True:
            _, data = await self.redis.blpop(self.MESSAGES_LIST)
            message = self._parse_message(data)
            logger.debug("Got new message %s", message)

            if handler := getattr(self, f"process_{message.type}", None):
                asyncio.create_task(handler(message))
            else:
                logger.warning("No handler for message type %s", message.type)

    @staticmethod
    def _parse_message(data: bytes) -> Message:
        parsed_data = json.loads(data.decode("utf8"))
        return Message.from_dict(parsed_data)

    async def process_user_event(self, message) -> None:
        await self.telegram_client.post_message(-641166626, message.payload["message"])

    async def process_bot_account_linked(self, message) -> None:
        await self.telegram_client.post_message(-641166626, "New bot account linked!")
