from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.db.models import Base


class DatabaseHandler:
    def __init__(self, url: str):
        self.url = url
        self.engine = create_async_engine(
            self.url,
            echo=False,
        )
        self.sessionmaker = async_sessionmaker(
            self.engine, autoflush=False, autocommit=False
        )

    async def init(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close_connection(self):
        await self.engine.dispose()
