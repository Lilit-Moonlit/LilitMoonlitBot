import asyncio
from app.database.dal import async_session
from app.database.models import Service
from sqlalchemy import update, select

async def seed_popularity():
    print("Starting initial popularity seeding...")
    async with async_session() as session:
        # 1. Отримуємо всі послуги
        result = await session.execute(select(Service))
        services = result.scalars().all()
        
        for s in services:
            pop = 10  # базове значення
            
            # Знижуємо популярність для "Видалення"
            if "видалення" in s.name.lower():
                pop = 1
            
            # Підвищуємо для основних категорій (наприклад, Манікюр, Стрижка, Тату)
            elif any(x in s.name.lower() for x in ["манікюр", "стрижка", "татуювання", "масаж", "пірсінг"]):
                pop = 100
            
            elif any(x in s.name.lower() for x in ["педикюр", "фарбування", "брови", "вії"]):
                pop = 50
                
            await session.execute(
                update(Service)
                .where(Service.id == s.id)
                .values(popularity=pop)
            )
            print(f"Set popularity={pop} for service ID: {s.id}")
            
        await session.commit()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(seed_popularity())
