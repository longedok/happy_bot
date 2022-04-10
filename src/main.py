#!/usr/bin/env python3
from __future__ import annotations

import logging

from redis import Redis

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


def main() -> None:
    init_logging()

    client = Client()
    redis = Redis(host="redis", port=6379, db=0, encoding="utf8")

    pubsub = RedisPubSub(client, redis)
    pubsub.start()

    bot = Bot(client)
    bot.start()


if __name__ == "__main__":
    main()
