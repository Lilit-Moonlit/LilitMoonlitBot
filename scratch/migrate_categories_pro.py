import asyncio
import os
import sys
from sqlalchemy import update, select

# Додаємо поточну директорію до path, щоб імпортувати app
sys.path.append(os.getcwd())

from app.database import dal
from app.database.models import Service

async def migrate():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("Starting database migration for categories...")
    
    # Мапа перейменування категорій
    MAPPING = {
        "Обличча": "Обличчя",
        "Брови та вії": "Вії та брови",
        "Додатково": "✨Інше",
        "Епіляція/депіляція": "Епіляція",
        "Інше": "✨Інше",
        "Косметологія": "Обличчя",
        "Тіло": "✨Інше"
    }
    
    async with dal.async_session() as session:
        for old_cat, new_cat in MAPPING.items():
            result = await session.execute(
                update(Service)
                .where(Service.category == old_cat)
                .values(category=new_cat)
            )
            count = result.rowcount
            if count > 0:
                print(f"Migrated {count} services from '{old_cat}' to '{new_cat}'")
        
        await session.commit()
    
    print("Database migration completed!")

if __name__ == "__main__":
    asyncio.run(migrate())
