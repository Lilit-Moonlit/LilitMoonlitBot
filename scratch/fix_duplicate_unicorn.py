import asyncio
import os
import sys
from sqlalchemy import update

# Додаємо поточну директорію до path, щоб імпортувати app
sys.path.append(os.getcwd())

from app.database import dal
from app.database.models import Service

async def migrate():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("Starting database migration to fix duplicate unicorn emoji...")
    
    async with dal.async_session() as session:
        result = await session.execute(
            update(Service)
            .where(Service.category == "🦄Інше")
            .values(category="Інше")
        )
        count = result.rowcount
        print(f"Migrated {count} services from '🦄Інше' to 'Інше'")
        
        await session.commit()
    
    print("Database migration completed!")

if __name__ == "__main__":
    asyncio.run(migrate())
