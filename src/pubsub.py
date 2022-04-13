from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db import async_session
from models import UserOrm
from telegram_client import TelegramClient

if TYPE_CHECKING:
    from aioredis import Redis


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

    def __init__(self, telegram_client: TelegramClient, redis: Redis) -> None:
        self.telegram_client = telegram_client
        self.redis = redis

    async def run(self) -> None:
        while True:
            _, data = await self.redis.blpop(self.MESSAGES_LIST)
            event = self._parse_event(data)
            logger.debug("Got new event %s", event)

            if handler := getattr(self, f"process_{event.type}", None):
                asyncio.create_task(handler(event))
            else:
                logger.warning("No handler for message type %s", event.type)

    @staticmethod
    def _parse_event(data: bytes) -> Event:
        parsed_data = json.loads(data.decode("utf8"))
        return Event.from_dict(parsed_data)

    async def process_user_event(self, event) -> None:
        async with async_session() as session:
            query = (
                select(UserOrm)
                .where(UserOrm.webapp_id == event.payload["user_id"])
                .options(joinedload(UserOrm.chats))
            )
            result = await session.execute(query)
            user = result.scalars().first()
            await session.commit()

        if not user:
            return

        await self.telegram_client.post_message(
            user.chats[0].telegram_id, event.payload["message"]
        )

    async def process_bot_account_linked(self, event) -> None:
        async with async_session() as session:
            query = (
                select(UserOrm)
                .where(UserOrm.token == event.payload["token"])
                .options(joinedload(UserOrm.chats))
            )
            result = await session.execute(query)
            if user := result.scalars().first():
                user.webapp_id = event.payload["user_id"]
                user.activated_at = datetime.now()
                session.add(user)
            await session.commit()

        if not user:
            pass

        await self.telegram_client.post_message(
            user.chats[0].telegram_id,
            "Your happiness-mj.xyz accounts has been linked successfully!",
        )
