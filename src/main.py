#!/usr/bin/env python3
from __future__ import annotations

import logging
import asyncio

import aioredis

from bot import Bot
from client import Client
from pubsub import RedisPubSub
from utils.logging import CustomFormatter


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

    client = Client()
    redis = aioredis.from_url("redis://redis", encoding="utf-8")

    pubsub = RedisPubSub(client, redis)

    bot = Bot(client)

    await asyncio.gather(
        bot.start(),
        pubsub.run(),
    )


if __name__ == "__main__":
    asyncio.run(main())
