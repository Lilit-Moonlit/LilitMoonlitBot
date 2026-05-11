import asyncio
from app.database.dal import async_session
from app.database.models import Service
from sqlalchemy import select

async def check():
    async with async_session() as session:
        query = await session.execute(select(Service).where(Service.name == 'Нарощування'))
        services = query.scalars().all()
        for s in services:
            print(f"{s.id}: {s.name} ({s.category})")

if __name__ == "__main__":
    asyncio.run(check())
