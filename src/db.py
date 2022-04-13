import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Base

pg_user = os.environ["BOT_POSTGRES_USERNAME"]
pg_pass = os.environ["BOT_POSTGRES_PASSWORD"]
pg_db = os.environ["BOT_POSTGRES_DB"]
pg_host = os.environ.get("POSTGRES_HOST", "postgres")

engine = create_async_engine(
    f"postgresql+asyncpg://{pg_user}:{pg_pass}@{pg_host}/{pg_db}",
    future=True
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, future=True,
)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
