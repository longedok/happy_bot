from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Type

from client import Client
from entities import Message

if TYPE_CHECKING:
    from bot_context import BotContext
    from entities import Command
    from validators import Validator


logger = getLogger(__name__)


class CommandHandlerRegistry(type):
    command_handlers: dict[str, Type[CommandHandler]] = {}
    callback_handlers: dict[str, Type[CommandHandler]] = {}

    def __new__(cls, name, bases, dct) -> CommandHandlerRegistry:
        handler_cls = super().__new__(cls, name, bases, dct)
        if hasattr(handler_cls, "command_str"):
            cls.command_handlers[handler_cls.command_str] = handler_cls
        if hasattr(handler_cls, "callback_type"):
            cls.callback_handlers[handler_cls.callback_type] = handler_cls
        return handler_cls

    @classmethod
    def get_for_command_str(cls, command_str: str) -> Type[CommandHandler] | None:
        return cls.command_handlers.get(command_str)

    @classmethod
    def get_for_callback_type(cls, callback_type: str) -> Type[CommandHandler] | None:
        return cls.callback_handlers.get(callback_type)

    @classmethod
    def get_public_handlers(cls) -> list[Type[CommandHandler]]:
        handlers = []
        for handler_class in cls.command_handlers.values():
            if getattr(handler_class, "short_description", None):
                handlers.append(handler_class)

        return handlers


class CommandHandler(metaclass=CommandHandlerRegistry):
    validator_class: Type[Validator] | None = None
    validator: Validator | None

    def __init__(
        self, client: Client, context: BotContext
    ) -> None:
        self.client = client
        self.context = context
        if self.validator_class:
            self.validator = self.validator_class()
        else:
            self.validator = None

    async def process(self, message: Message) -> None:
        raise NotImplementedError

    def validate(self, command: Command) -> None:
        if self.validator:
            self.validator.validate(command)


class LinkHandler(CommandHandler):
    command_str = "link"
    short_description = "Link your happiness-mj.xyz account."

    async def process(self, message: Message) -> None:
        pass


class PingHandler(CommandHandler):
    command_str = "ping"
    short_description = 'Sends "pong" in response.'

    async def process(self, message: Message) -> None:
        await self.client.reply(message, f"pong")


class GithubHandler(CommandHandler):
    command_str = "github"
    short_description = 'Sends github link.'

    async def process(self, message: Message) -> None:
        await self.client.reply(
            message,
            f"Coming soon...",
            disable_web_page_preview=True,
        )


class HelpHandler(CommandHandler):
    command_str = "help"
    short_description = "Display help message."

    HELP = """Happy bot."""

    async def process(self, message: Message) -> None:
        await self.client.reply(message, self.HELP)
