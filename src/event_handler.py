from __future__ import annotations

from datetime import datetime
from logging import getLogger

from pubsub import Event
from repositories import UserRepository
from task_manager import TaskManager
from telegram_client import TelegramClient

logger = getLogger(__name__)


class EventHandler:
    MAX_PARALLEL_TASKS = 5

    def __init__(
        self,
        telegram_client: TelegramClient,
        user_repository: UserRepository,
    ) -> None:
        self.telegram_client = telegram_client
        self.user_repository = user_repository
        self.task_manager = TaskManager(self.MAX_PARALLEL_TASKS)

    async def handle(self, event: Event) -> None:
        logger.debug("Got new event %s", event)

        if handler := getattr(self, f"process_{event.type}", None):
            await self.task_manager.run_task(handler(event))
        else:
            logger.warning("No handler for event type %s", event.type)

    async def process_user_event(self, event: Event) -> None:
        user = await self.user_repository.get_by_webapp_id_with_chats(
            event.payload["user_id"]
        )

        if not user:
            return

        await self.telegram_client.post_message(
            user.chat.telegram_id, event.payload["message"]
        )

    async def process_bot_account_linked(self, event: Event) -> None:
        token = event.payload["token"]
        if user := await self.user_repository.get_by_token_with_chats(token):
            user.webapp_id = event.payload["user_id"]
            user.activated_at = datetime.now()
            await self.user_repository.update(user)
        else:
            return None

        await self.telegram_client.post_message(
            user.chat.telegram_id,
            "Your happiness-mj.xyz account has been linked successfully!",
        )
