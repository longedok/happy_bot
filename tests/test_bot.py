import copy
import random
import re
from datetime import datetime
from functools import cached_property
from unittest.mock import MagicMock, Mock

import pytest

from bot import Bot
from command_handlers import HelpHandler

CHAT_ID = -593555199

UPDATE = {
    "update_id": 360316438,
    "message": {
        "message_id": 125,
        "from": {
            "id": 427258479,
            "is_bot": False,
            "first_name": "Иван",
            "username": "iivanov",
        },
        "chat": {
            "id": CHAT_ID,
            "title": "Bot Test (dev)",
            "type": "group",
            "all_members_are_administrators": True,
        },
        "date": 1612207828,
        "text": "Hello World!",
    },
}


def make_message(text):
    body = copy.deepcopy(UPDATE)
    body["message"]["text"] = text

    re_to_type = {
        r"/\w*\b": "bot_command",
        r"#\w*\b": "hashtag",
    }

    entities = []
    for regexp, entity_type in re_to_type.items():
        for match in re.finditer(regexp, text):
            start, end = match.span()
            entities.append(
                {
                    "offset": start,
                    "length": end - start,
                    "type": entity_type,
                }
            )

    if entities:
        body["message"]["entities"] = entities

    return body


def new_message(bot, text):
    message = make_message(text)
    bot.client.get_updates = Mock(side_effect=[[message], KeyboardInterrupt])
    bot.start()
    return message


def get_response(client):
    return client.reply.call_args.args


@pytest.fixture
def client():
    return Mock()


class FakeMessageRecord:
    @cached_property
    def message_id(self):
        return random.randint(1000, 10000)

    @cached_property
    def delete_after(self):
        return int(datetime.utcnow().timestamp()) + random.randint(100, 1000)


class FakeQuery:
    def __init__(self, records=None) -> None:
        self.records = records if records is not None else []

    def offset(self, *args):
        return self

    def limit(self, *args):
        return self

    def count(self):
        return len(self.records)

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.records):
            record = self.records[self.n]
            self.n += 1
            return record
        else:
            raise StopIteration

    @classmethod
    def populate(cls, n):
        return cls([FakeMessageRecord() for _ in range(n)])


class TestBot:
    @pytest.fixture
    def bot(self, client):
        return Bot(client)

    def test_ping(self, bot):
        new_message(bot, "/ping")

        message, text = get_response(bot.telegram_client)
        assert message.chat.id == CHAT_ID
        assert text == "pong"

    def test_help(self, bot):
        new_message(bot, "/help")

        message, text = get_response(bot.telegram_client)
        assert message.chat.id == CHAT_ID
        assert text == HelpHandler.HELP

    def test_username_command(self, bot):
        bot.USERNAME = "happy_mj_bot"
        new_message(bot, "/ping@happy_mj_bot")

        message, text = get_response(bot.telegram_client)
        assert message.chat.id == CHAT_ID
        assert text == "pong"

    def test_invalid_command(self, bot):
        new_message(bot, "/invalid")

        message, text = get_response(bot.telegram_client)
        assert message.chat.id == CHAT_ID
        assert "unrecognized command" in text.lower()
