from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

from bot_context import BotContext
from command_handlers import CommandHandlerRegistry
from entities import CallbackQuery, Command, Message
from exceptions import ValidationError
from webapp_client import WebappClient

if TYPE_CHECKING:
    from entities import ForwardFromChat
    from telegram_client import TelegramClient as TelegramClient

logger = logging.getLogger(__name__)


class Bot:
    USERNAME = os.environ.get("BOT_USERNAME", "gcservantbot")

    def __init__(
        self, telegram_client: TelegramClient, webapp_client: WebappClient
    ) -> None:
        self.telegram_client = telegram_client
        self.webapp_client = webapp_client
        self.context = BotContext()

    async def start(self) -> None:
        # await self.set_my_commands()  # TODO: enable
        await self.run_polling_loop()

    async def set_my_commands(self) -> None:
        logger.info("Setting bot's command list")
        handlers = CommandHandlerRegistry.get_public_handlers()
        commands = []
        for handler in handlers:
            commands.append(
                {
                    "command": handler.command_str,
                    "description": handler.short_description,
                }
            )
        await self.telegram_client.set_my_commands(commands)

    async def run_polling_loop(self) -> None:
        logger.info("Starting the polling loop")
        while True:
            try:
                updates = await self.telegram_client.get_updates()
            except KeyboardInterrupt:
                logger.info("Exiting...")
                return

            for update in updates:
                asyncio.create_task(self.process_update(update))

            if updates:
                logger.debug("%d update(s) received", len(updates))

    async def process_update(self, update: dict) -> None:
        logger.debug("Processing new update: %s", update)

        if "message" in update:
            message = Message.from_json(update["message"])
            await self.process_message(message)
        # elif "callback_query" in update:
        #     callback = CallbackQuery.from_json(update["callback_query"])
        #     await self.process_callback(callback)

    async def process_message(self, message: Message) -> None:
        logger.debug("New %s", message)

        if forward_from_chat := message.forward_from_chat:
            if await self.process_forward_message(message, forward_from_chat):
                return
        elif command := message.command:
            if await self.process_command_message(message, command):
                return
        elif tags := message.get_tags():
            if await self.process_tags(message, tags):
                return

    async def process_callback(self, callback: CallbackQuery) -> None:
        logger.debug("New %s", callback)

        callback_type = callback.data.get("type")
        if callback_type is None:
            logger.error("Received a CallbackQuery with wrong structure: %s", callback)
            return

        handler_class = CommandHandlerRegistry.get_for_callback_type(callback_type)
        if handler_class:
            handler = handler_class(self.telegram_client, self.context)
            await handler.process_callback(callback)

    async def process_command_message(self, message: Message, command: Command) -> bool:
        if command.entity.offset != 0:
            return False

        if command.username and command.username != self.USERNAME:
            logger.debug(
                "Received a command that's meant for another bot: %s@%s",
                command.command_str,
                command.username,
            )
            return False

        handler_class = CommandHandlerRegistry.get_for_command_str(command.command_str)
        if not handler_class:
            await self.telegram_client.reply(
                message, f"Unrecognized command: {command.command_str}"
            )
            return False

        handler = handler_class(self.telegram_client, self.webapp_client, self.context)
        try:
            handler.validate(command)
        except ValidationError as exc:
            await self.telegram_client.reply(message, exc.message)
            return True

        await handler.process(message)

        return True

    async def process_forward_message(
        self,
        message: Message,
        forward_from_chat: ForwardFromChat,
    ) -> bool:
        return False

    async def process_tags(self, message: Message, tags: list[str]) -> bool:
        return False
