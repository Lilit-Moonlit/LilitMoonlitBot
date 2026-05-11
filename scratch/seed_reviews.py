import asyncio
import os
import sys
from datetime import datetime

# Додаємо поточну директорію до path, щоб імпортувати app
sys.path.append(os.getcwd())

from app.database import dal
from app.database.models import RoleEnum

async def seed():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("Seeding reviews for testing...")
    
    # 1. Знаходимо майстра і клієнта
    # Припустимо, у нас є майстер з ID 162985838 (це може бути ваш ID)
    # Або просто візьмемо першого ліпшого майстра з бази
    async with dal.async_session() as session:
        from sqlalchemy import select
        from app.database.models import Master, User, Booking, MasterService
        
        master_res = await session.execute(select(Master).limit(1))
        master = master_res.scalars().first()
        if not master:
            print("No masters found in DB. Please register at least one master first.")
            return
            
        client_res = await session.execute(select(User).where(User.telegram_id != master.user_id).limit(1))
        client = client_res.scalars().first()
        if not client:
            # Створимо фейкового клієнта
            client = await dal.create_user(999, "Тестовий Клієнт", RoleEnum.CLIENT)
            
        # 2. Створюємо завершений букінг для відгуку
        ms_res = await session.execute(select(MasterService).where(MasterService.master_id == master.user_id).limit(1))
        ms = ms_res.scalars().first()
        
        from app.database.models import BookingStatusEnum
        booking = Booking(
            client_id=client.telegram_id,
            master_id=master.user_id,
            master_service_id=ms.id,
            start_time=datetime.now(),
            end_time=datetime.now(),
            status=BookingStatusEnum.COMPLETED
        )
        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        
        # 3. Додаємо відгуки
        reviews_data = [
            (5, "Дуже сподобалось! Майстер професіонал."),
            (4, "Все добре, але довелось трохи почекати."),
            (5, "Найкращий манікюр у моєму житті! ⭐⭐⭐⭐⭐")
        ]
        
        for rating, comment in reviews_data:
            # Створимо окремі букінги для кожного відгуку, бо dal.add_booking_review прив'язаний до booking_id
            b = Booking(
                client_id=client.telegram_id,
                master_id=master.user_id,
                master_service_id=ms.id,
                start_time=datetime.now(),
                end_time=datetime.now(),
                status=BookingStatusEnum.COMPLETED
            )
            session.add(b)
            await session.commit()
            await session.refresh(b)
            await dal.add_booking_review(b.id, RoleEnum.CLIENT, rating, comment)
            
    print("Seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
