import asyncio
from app.database.dal import async_session
from app.database.models import Service
from sqlalchemy import select

async def check():
    async with async_session() as s:
        res = await s.execute(select(Service.category).distinct())
        cats = res.scalars().all()
        print(f"Categories found: {cats}")
        
        res = await s.execute(select(Service))
        services = res.scalars().all()
        print(f"Total services: {len(services)}")
        if services:
            print(f"First service: {services[0].name} in {services[0].category}")

if __name__ == "__main__":
    asyncio.run(check())
