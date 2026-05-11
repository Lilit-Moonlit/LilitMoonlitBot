import asyncio
from sqlalchemy import select
from app.database.dal import async_session
from app.database.models import Service

async def migrate_services():
    async with async_session() as session:
        query = await session.execute(select(Service).where(Service.category == 'Вії та брови'))
        services = query.scalars().all()
        for s in services:
            if "брів" in s.name.lower():
                print(f"Moving {s.name} to Брови")
                s.category = "Брови"
            elif "вій" in s.name.lower() or "вії" in s.name.lower():
                print(f"Moving {s.name} to Вії")
                s.category = "Вії"
            else:
                print(f"Unknown category for {s.name}")
        await session.commit()
        print("Migration complete.")

if __name__ == "__main__":
    asyncio.run(migrate_services())
