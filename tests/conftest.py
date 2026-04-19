import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database.models import Base
from app.database import dal

# Використовуємо окрему базу для тестів
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_beauty_bot.db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

# Перевизначаємо dal.async_session для тестів
@pytest.fixture(autouse=True)
def override_dal_session(test_engine):
    original_sessionmaker = dal.async_session
    dal.async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    yield
    dal.async_session = original_sessionmaker
