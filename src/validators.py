from __future__ import annotations

from entities import Command


class Validator:
    def validate(self, command: Command) -> None:
        raise NotImplementedError
