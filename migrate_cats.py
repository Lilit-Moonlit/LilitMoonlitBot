import asyncio
from app.database.dal import async_session
from app.database.models import Service
from sqlalchemy import update

async def migrate_categories():
    async with async_session() as session:
        # Оновити всі послуги з категорією "Обличчя" на "Вії та брови"
        await session.execute(
            update(Service)
            .where(Service.category == "Обличчя")
            .values(category="Вії та брови")
        )
        await session.commit()
    print("Migration completed: 'Обличчя' -> 'Вії та брови'")

if __name__ == "__main__":
    asyncio.run(migrate_categories())
