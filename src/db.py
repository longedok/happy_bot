import os
from asyncio import current_task
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from logging import getLogger
from typing import Callable

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from models import Base

logger = getLogger(__name__)


pg_user = os.environ["BOT_POSTGRES_USERNAME"]
pg_pass = os.environ["BOT_POSTGRES_PASSWORD"]
pg_db = os.environ["BOT_POSTGRES_DB"]
pg_host = os.environ.get("POSTGRES_HOST", "postgres")

DB_URL = f"postgresql+asyncpg://{pg_user}:{pg_pass}@{pg_host}/{pg_db}"


SessionFactory = Callable[..., AbstractAsyncContextManager[Session]]


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, future=True)
        self._session_factory = async_scoped_session(
            sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                future=True,
            ),
            current_task,
        )

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> SessionFactory:
        session: AsyncSession = self._session_factory()

        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()
