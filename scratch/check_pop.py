import asyncio
from app.database.dal import async_session
from app.database.models import Service
from sqlalchemy import select

async def check_db():
    async with async_session() as session:
        print("--- Services in 'Other' category ---")
        res = await session.execute(
            select(Service)
            .where(Service.category == "Інше")
            .order_by(Service.popularity.desc())
        )
        for s in res.scalars().all():
            # encode to avoid console errors
            safe_name = s.name.encode('ascii', 'ignore').decode('ascii')
            print(f"ID: {s.id} | Name: {safe_name} | Pop: {s.popularity}")

if __name__ == "__main__":
    asyncio.run(check_db())
