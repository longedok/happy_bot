from __future__ import annotations

__version__ = "0.1.0"

from datetime import datetime
from typing import TYPE_CHECKING

from utils.formatting import format_interval

if TYPE_CHECKING:
    from datetime import timedelta


class BotContext:
    def __init__(self) -> None:
        self.start_at = datetime.now()
        self.version = __version__

    def get_uptime(self) -> timedelta:
        return datetime.now() - self.start_at

    def status(self) -> dict:
        return {
            "uptime": format_interval(self.get_uptime()),
            "version": self.version,
        }

