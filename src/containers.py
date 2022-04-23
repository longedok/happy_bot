import aioredis
from dependency_injector import containers, providers

from bot import Bot
from db import DB_URL, Database
from event_handler import EventHandler
from pubsub import RedisPubSub
from repositories import UserRepository
from telegram_client import TelegramClient
from webapp_client import WebappClient


class Container(containers.DeclarativeContainer):
    telegram_client = providers.Singleton(TelegramClient)
    webapp_client = providers.Singleton(WebappClient)
    db = providers.Singleton(
        Database,
        db_url=DB_URL,
    )
    redis = providers.Singleton(
        aioredis.from_url,
        "redis://redis",
        encoding="utf-8",
    )
    user_repository = providers.Factory(
        UserRepository,
        session_factory=db.provided.session,
    )
    event_handler = providers.Factory(
        EventHandler,
        telegram_client=telegram_client,
        user_repository=user_repository,
    )
    redis_pubsub = providers.Singleton(
        RedisPubSub,
        event_handler=event_handler,
        redis=redis,
    )
    bot = providers.Singleton(
        Bot,
        telegram_client=telegram_client,
        webapp_client=webapp_client,
        user_repository=user_repository,
    )
