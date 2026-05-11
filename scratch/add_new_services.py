import asyncio
import os
import sys
from sqlalchemy import select

# Додаємо поточну директорію до path, щоб імпортувати app
sys.path.append(os.getcwd())

from app.database import dal
from app.database.models import Service

async def migrate():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("Starting database migration for new services...")
    
    services_to_add = [
        ("Перм. макіяж брів", "Брови"),
        ("Ботокс, кератин", "Брови"),
        ("Перм. макіяж", "Обличчя"),
        ("Зняття вій", "Вії"),
        ("Біозавивка", "Вії"),
        ("Ботокс, кератин", "Вії"),
        ("Контурна пластика", "Губи")
    ]
    
    async with dal.async_session() as session:
        for name, category in services_to_add:
            # Check if service already exists in that category
            result = await session.execute(
                select(Service)
                .where(Service.name == name)
                .where(Service.category == category)
            )
            existing = result.scalars().first()
            if not existing:
                new_service = Service(name=name, category=category)
                session.add(new_service)
                print(f"Added new service: {name} in {category}")
            else:
                print(f"Service {name} already exists in {category}")
        
        await session.commit()
    
    print("Database migration completed!")

if __name__ == "__main__":
    asyncio.run(migrate())
