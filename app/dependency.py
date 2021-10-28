import gino

from app.config import config

engine = gino.create_engine(str(config.db_dsn))


async def get_db():
    """Дублирование сессии для работы в отдельном потоке."""

    async with engine.acquire() as session:
        yield session
