import asyncio
from sqlalchemy import select
from app.database.dal import async_session
from app.database.models import Service

async def main():
    async with async_session() as session:
        query = await session.execute(select(Service).where(Service.category == 'Вії та брови'))
        services = query.scalars().all()
        for s in services:
            print(f"{s.id}: {s.name}")

if __name__ == "__main__":
    asyncio.run(main())
