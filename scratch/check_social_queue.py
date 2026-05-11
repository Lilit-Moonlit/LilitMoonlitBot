import asyncio
from app.database.dal import async_session
from app.database.models import SocialPostQueue
from sqlalchemy import select

async def check_queue():
    async with async_session() as session:
        result = await session.execute(select(SocialPostQueue).order_by(SocialPostQueue.created_at.desc()).limit(10))
        posts = result.scalars().all()
        
        print(f"{'ID':<5} | {'Type':<10} | {'Status':<10} | {'Created At':<20} | {'Error'}")
        print("-" * 80)
        for p in posts:
            error = (p.error_message[:40] + "...") if p.error_message and len(p.error_message) > 40 else (p.error_message or "")
            print(f"{p.id:<5} | {p.ad_type:<10} | {p.status:<10} | {p.created_at.strftime('%H:%M:%S'):<20} | {error}")

if __name__ == "__main__":
    asyncio.run(check_queue())
