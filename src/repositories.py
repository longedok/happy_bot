from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db import SessionFactory
from models import UserOrm


class UserRepository:
    def __init__(self, session_factory: SessionFactory) -> None:
        self.session_factory = session_factory

    async def get_by_token_with_chats(self, token: str) -> UserOrm | None:
        async with self.session_factory() as session:
            query = (
                select(UserOrm)
                .where(UserOrm.token == token)
                .options(joinedload(UserOrm.chats))
            )
            result = await session.execute(query)
            return result.scalars().first()

    async def get_by_webapp_id_with_chats(self, webapp_id: int) -> UserOrm | None:
        async with self.session_factory() as session:
            query = (
                select(UserOrm)
                .where(UserOrm.webapp_id == webapp_id)
                .options(joinedload(UserOrm.chats))
            )
            result = await session.execute(query)
            return result.scalars().first()

    async def update(self, user: UserOrm) -> None:
        async with self.session_factory() as session:
            session.add(user)
            await session.commit()

    async def update_all(self, *objects: Any) -> None:
        async with self.session_factory() as session:
            session.add_all(objects)
            await session.commit()

    async def get_by_telegram_id(self, telegram_id: int) -> UserOrm | None:
        async with self.session_factory() as session:
            query = select(UserOrm).where(UserOrm.telegram_id == telegram_id)
            result = await session.execute(query)
            return result.scalars().first()
