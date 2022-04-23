#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import logging

from dependency_injector.wiring import Provide, inject

from bot import Bot
from containers import Container
from db import Database
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
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


@inject
async def main(
    bot: Bot = Provide[Container.bot],
    db: Database = Provide[Container.db],
    redis_pubsub: RedisPubSub = Provide[Container.redis_pubsub],
) -> None:
    init_logging()
    await db.create_database()
    await asyncio.gather(bot.start(), redis_pubsub.run())


if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    asyncio.run(main())
