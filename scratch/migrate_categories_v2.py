
import asyncio
import json
from sqlalchemy import select, update, delete
from app.database.models import Service
from app.database.dal import async_session

NEW_CATEGORIES = [
    "Волосся",
    "Нігті",
    "Вії та брови",
    "Косметологія",
    "Масаж",
    "SPA",
    "Видалення волосся",
    "Додатково"
]

CATEGORY_MAPPING = {
    "Перукарські послуги": "Волосся",
    "Волосся": "Волосся",
    "Нігтьовий сервіс": "Нігті",
    "Нігті": "Нігті",
    "Брови та вії": "Вії та брови",
    "Вії та брови": "Вії та брови",
    "Косметологічні послуги": "Косметологія",
    "Косметологія": "Косметологія",
    "Депіляція": "Видалення волосся",
    "Масаж": "Масаж",
    "SPA-процедури": "SPA",
    "Інше": "Додатково"
}

# Спеціальна обробка для категорії "Тіло"
TILO_MAPPING = {
    "Масаж класичний": "Масаж",
    "Антицелюлітний масаж": "Масаж",
    "Лімфодренажний масаж": "Масаж",
    "Масаж спини": "Масаж",
    "Лазерна епіляція (ноги)": "Видалення волосся",
    "Шугаринг (бікіні)": "Видалення волосся",
    "Воскова депіляція": "Видалення волосся",
    "Обгортання тіла": "SPA"
}

async def migrate():
    async with async_session() as session:
        # 1. Проста міграція по мапі
        for old_cat, new_cat in CATEGORY_MAPPING.items():
            await session.execute(
                update(Service)
                .where(Service.category == old_cat)
                .values(category=new_cat)
            )
        
        # 2. Обробка категорії "Тіло" (вона занадто загальна)
        for s_name, new_cat in TILO_MAPPING.items():
            await session.execute(
                update(Service)
                .where(Service.category == "Тіло", Service.name == s_name)
                .values(category=new_cat)
            )
            
        # Якщо в "Тіло" залишилось щось невраховане — переносимо в "Додатково"
        await session.execute(
            update(Service)
            .where(Service.category == "Тіло")
            .values(category="Додатково")
        )
        
        # 3. Створення "Інше" для кожної категорії
        for cat in NEW_CATEGORIES:
            # Перевіримо чи вже є
            res = await session.execute(
                select(Service).where(Service.category == cat, Service.name == "Інше")
            )
            if not res.scalars().first():
                new_s = Service(name="Інше", category=cat)
                session.add(new_s)
        
        await session.commit()
    print("Migration of categories completed!")

if __name__ == "__main__":
    asyncio.run(migrate())
