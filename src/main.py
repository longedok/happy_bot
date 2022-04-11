#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import logging

import aioredis

from bot import Bot
from pubsub import RedisPubSub
from telegram_client import TelegramClient
from utils.logging import CustomFormatter
from webapp_client import WebappClient


def init_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-5s %(name)-16s > %(message)s",
        level=logging.DEBUG,
    )

    logger = logging.getLogger()
    for handler in logger.root.handlers:  # type: ignore
        handler.setFormatter(CustomFormatter(handler.formatter._fmt))


async def main() -> None:
    init_logging()

    telegram_client = TelegramClient()
    webapp_client = WebappClient()
    redis = aioredis.from_url("redis://redis", encoding="utf-8")

    pubsub = RedisPubSub(telegram_client, redis)

    bot = Bot(telegram_client, webapp_client)

    await asyncio.gather(
        bot.start(),
        pubsub.run(),
    )


if __name__ == "__main__":
    asyncio.run(main())
