import asyncio
import random
from app.database.dal import async_session, engine
from app.database.models import Base, User, Master, Service, MasterService, RoleEnum
from sqlalchemy import select

async def seed_data():
    from app.catalog import SERVICE_CATALOG
    
    # 0. Створюємо таблиці
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as session:
        # 1. Створюємо послуги з офіційного каталогу
        print("Seeding services from official catalog...")
        db_services_count = 0
        for category, services in SERVICE_CATALOG.items():
            for name in services:
                # Перевіряємо чи вже є така послуга
                s_q = await session.execute(select(Service).where(Service.name == name, Service.category == category))
                service = s_q.scalars().first()
                if not service:
                    service = Service(name=name, category=category)
                    session.add(service)
                    db_services_count += 1
        
        await session.commit()
        print(f"Database seeded with {db_services_count} official services.")

if __name__ == "__main__":
    asyncio.run(seed_data())
