import asyncio
from sqlalchemy import text, delete
from app.database.dal import async_session, engine
from app.database.models import User, Master, MasterService, Booking

async def clean_test_data():
    async with async_session() as session:
        print("Cleaning test masters and users...")
        
        # Видаляємо записи, де telegram_id >= 1000000 (це наші фейкові майстри з seed.py)
        # Спочатку видаляємо залежні дані
        await session.execute(text("DELETE FROM bookings WHERE master_id >= 1000000 OR client_id >= 1000000"))
        await session.execute(text("DELETE FROM master_services WHERE master_id >= 1000000"))
        await session.execute(text("DELETE FROM masters WHERE user_id >= 1000000"))
        await session.execute(text("DELETE FROM users WHERE telegram_id >= 1000000"))
        
        await session.commit()
        print("Cleanup complete. All test masters removed.")

if __name__ == "__main__":
    asyncio.run(clean_test_data())
