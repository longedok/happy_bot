from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta
from logging import getLogger
from typing import TYPE_CHECKING, Type, cast

from entities import Message
from models import ChatOrm, UserOrm
from repositories import UserRepository
from telegram_client import TelegramClient
from webapp_client import WebappClient

if TYPE_CHECKING:
    from bot_context import BotContext
    from entities import Command
    from validators import Validator


logger = getLogger(__name__)


class CommandHandlerRegistry(type):
    command_handlers: dict[str, Type[CommandHandler]] = {}

    def __new__(
        mcs: Type[CommandHandlerRegistry], name: str, bases: tuple, dct: dict
    ) -> CommandHandlerRegistry:
        handler_cls: Type[CommandHandler] = super().__new__(mcs, name, bases, dct)
        if hasattr(handler_cls, "command_str"):
            mcs.command_handlers[handler_cls.command_str] = handler_cls
        return cast(CommandHandlerRegistry, handler_cls)

    @classmethod
    def get_for_command_str(mcs, command_str: str) -> Type[CommandHandler] | None:
        return mcs.command_handlers.get(command_str)

    @classmethod
    def get_public_handlers(mcs) -> list[Type[CommandHandler]]:
        handlers = []
        for handler_class in mcs.command_handlers.values():
            if getattr(handler_class, "short_description", None):
                handlers.append(handler_class)

        return handlers


class CommandHandler(metaclass=CommandHandlerRegistry):
    validator_class: Type[Validator] | None = None
    validator: Validator | None

    def __init__(
        self,
        telegram_client: TelegramClient,
        webapp_client: WebappClient,
        user_repository: UserRepository,
        context: BotContext,
    ) -> None:
        self.telegram_client = telegram_client
        self.webapp_client = webapp_client
        self.context = context
        self.user_repository = user_repository
        if self.validator_class:
            self.validator = self.validator_class()
        else:
            self.validator = None

    async def process(self, message: Message) -> None:
        raise NotImplementedError

    def validate(self, command: Command) -> None:
        if self.validator:
            self.validator.validate(command)


def _get_date_from_seconds(seconds: int):
    return datetime.now() + timedelta(seconds=seconds)


class LinkHandler(CommandHandler):
    command_str = "link"
    short_description = "Link your happiness-mj.xyz account"

    WEB_APP_LINKS_BASE = os.environ.get("WEBAPP_LINKS_BASE")
    TOKEN_EXPIRATION_SECONDS = 1800  # 30 MIN

    async def _get_or_create_user_with_chat(
        self,
        user_telegram_id: int,
        chat_telegram_id: int,
    ) -> UserOrm:
        to_update = set()
        if not (
            user := await self.user_repository.get_by_telegram_id(user_telegram_id)
        ):
            user = UserOrm(
                telegram_id=user_telegram_id,
                token=str(uuid.uuid4()),
                token_expires_at=_get_date_from_seconds(self.TOKEN_EXPIRATION_SECONDS),
            )
            chat = ChatOrm(user=user, telegram_id=chat_telegram_id, type="private")
            to_update.update([user, chat])

        if user.token_expires_at > datetime.now():
            user.token_expires_at = _get_date_from_seconds(
                self.TOKEN_EXPIRATION_SECONDS
            )
            to_update.add(user)

        await self.user_repository.update_all(*to_update)

        return user

    async def process(self, message: Message) -> None:
        if message.chat.type != "private":
            await self.telegram_client.reply(
                message, f"This command is only available in private chats."
            )
            return None

        user = await self._get_or_create_user_with_chat(
            message.from_.id, message.chat.id
        )

        if user.is_active:
            await self.telegram_client.reply(
                message, f"Your account is already linked. You're all set up!"
            )
            return None

        result = await self.webapp_client.make_bot_token(user.token)
        logger.debug("Token created %s", result)

        url = result["url"]
        await self.telegram_client.reply(
            message,
            f"Follow this url to link your account - {self.WEB_APP_LINKS_BASE}{url}",
        )


class HelpHandler(CommandHandler):
    command_str = "help"
    short_description = "Get help on how to use the bot"

    HELP = """Happy bot."""

    async def process(self, message: Message) -> None:
        await self.telegram_client.reply(message, self.HELP)


class PingHandler(CommandHandler):
    command_str = "ping"
    short_description = "Test bot connectivity"

    async def process(self, message: Message) -> None:
        await self.telegram_client.reply(message, f"pong")
