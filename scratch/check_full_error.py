import asyncio
from app.database.dal import async_session
from app.database.models import SocialPostQueue
from sqlalchemy import select

async def check_full_error():
    async with async_session() as session:
        result = await session.execute(select(SocialPostQueue).where(SocialPostQueue.id == 1))
        p = result.scalars().first()
        if p:
            print(f"Post ID: {p.id}")
            print(f"Status: {p.status}")
            print(f"Error: {p.error_message}")

if __name__ == "__main__":
    asyncio.run(check_full_error())
