import asyncio
import sqlite3
import sys
import os
from datetime import datetime, timedelta

# Додаємо корінь проекту до шляху пошуку модулів
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import dal
from app.database.models import BookingStatusEnum

async def simulate_booking_flow():
    """
    Цей скрипт створює тестову ситуацію прямо у вашій основній базі,
    щоб ви могли перевірити нагадування та сповіщення.
    """
    print("🚀 Починаємо симуляцію потоку...")
    
    # 1. Знаходимо останнього користувача (вас, якщо ви натиснули /start)
    async with dal.async_session() as session:
        from sqlalchemy import select
        from app.database.models import User, Master, MasterService
        
        # Отримуємо останнього клієнта
        res = await session.execute(select(User).order_by(User.created_at.desc()))
        client = res.scalars().first()
        
        if not client:
            print("❌ Користувачів не знайдено. Будь ласка, натисніть /start у боті.")
            return

        print(f"✅ Знайдено клієнта: {client.name} (ID: {client.telegram_id})")

        # Отримуємо будь-якого майстра
        res = await session.execute(select(Master, User).join(User).limit(1))
        master_row = res.first()
        if not master_row:
            print("❌ Майстрів не знайдено. Спочатку зареєструйтесь як майстер.")
            return
        
        master, m_user = master_row
        print(f"✅ Вибрано майстра для тесту: {m_user.name}")

        # Отримуємо послугу майстра
        res = await session.execute(select(MasterService).where(MasterService.master_id == master.user_id).limit(1))
        ms = res.scalars().first()
        if not ms:
            print("❌ У обраного майстра немає послуг.")
            return

        # 2. Створюємо БРОНЮВАННЯ на «через 1 годину» (щоб спрацював scheduler)
        now = datetime.now().replace(second=0, microsecond=0)
        start_time = now + timedelta(hours=1)
        
        booking = await dal.create_booking(
            client_id=client.telegram_id,
            master_id=master.user_id,
            service_id=ms.id,
            start_time=start_time.strftime("%d.%m %H:%M")
        )
        
        # Ставимо статус CONFIRMED, щоб прийшло нагадування
        await dal.update_booking_status(booking.id, BookingStatusEnum.CONFIRMED)
        
        print(f"📅 Створено ПІДТВЕРДЖЕНИЙ запис на {start_time.strftime('%H:%M')}.")
        print(f"🔔 Нагадування має прийти рівно о {now.strftime('%H:%M')} (протягом хвилини).")
        print("\nПорада: Переконайтеся, що файл start.bat запущено!")

if __name__ == "__main__":
    asyncio.run(simulate_booking_flow())
