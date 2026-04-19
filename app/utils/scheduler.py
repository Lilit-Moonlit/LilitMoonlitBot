import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from aiogram import Bot
from app.database.dal import async_session
from app.database.models import Booking, User, BookingStatusEnum

kyiv_tz = pytz.timezone('Europe/Kyiv')
scheduler = AsyncIOScheduler(timezone=kyiv_tz)

async def send_reminders(bot):
    """
    Періодично перевіряє базу даних на наявність підтверджених записів, 
    до яких залишилось менше 1 години, і надсилає нагадування.
    """
    async with async_session() as session:
        now = datetime.now(kyiv_tz).replace(tzinfo=None)
        # Нагадування має прийти, якщо до візиту залишилось менше ніж 1 година
        remind_limit = now + timedelta(hours=1)
        
        # Шукаємо записи, які відбудуться незабаром і нагадування ще не було
        query = (
            select(Booking, User)
            .join(User, User.telegram_id == Booking.client_id)
            .where(Booking.status == BookingStatusEnum.CONFIRMED)
            .where(Booking.is_reminder_sent == False)
            .where(Booking.start_time <= remind_limit)
            .where(Booking.start_time > now)
        )
        
        result = await session.execute(query)
        bookings_to_remind = result.all()
        
        for booking, client in bookings_to_remind:
            try:
                time_str = booking.start_time.strftime("%H:%M")
                text = (
                    f"⏰ <b>Нагадування про візит!</b>\n\n"
                    f"Ви записані на сьогодні о <b>{time_str}</b>.\n"
                    f"Чекаємо на вас! ✨"
                )
                await bot.send_message(chat_id=client.telegram_id, text=text, parse_mode="HTML")
                
                # Помічаємо як надіслане
                booking.is_reminder_sent = True
            except Exception as e:
                print(f"[SCHEDULER ERROR] Could not send reminder to {client.telegram_id}: {e}")
        
        await session.commit()

def setup_scheduler(bot):    
    # Реєструємо задачу нагадувань (щохвилини)
    scheduler.add_job(send_reminders, 'interval', minutes=1, args=[bot])
    # Реєструємо задачу на відгуки (щохвилини)
    scheduler.add_job(check_finished_visits, 'interval', minutes=1, args=[bot])
    
    scheduler.start()

async def check_finished_visits(bot: Bot):
    """
    Шукає візити, які щойно завершилися, і просить залишити відгук.
    """
    async with async_session() as session:
        now = datetime.now(kyiv_tz).replace(tzinfo=None)
        # Шукаємо візити, які закінчилися принаймні 4 години тому
        review_trigger_time = now - timedelta(hours=4)
        
        query = (
            select(Booking)
            .where(Booking.status == BookingStatusEnum.CONFIRMED)
            .where(Booking.end_time <= review_trigger_time)
        )
        
        result = await session.execute(query)
        finished_bookings = result.scalars().all()
        
        for b in finished_bookings:
            # Оновлюємо статус на COMPLETED
            b.status = BookingStatusEnum.COMPLETED
            
            # Надсилаємо запит клієнту
            try:
                from aiogram.utils.keyboard import InlineKeyboardBuilder
                from aiogram.types import InlineKeyboardButton
                kb = InlineKeyboardBuilder()
                kb.row(InlineKeyboardButton(text="⭐ Залишити відгук", callback_data=f"review_visit_{b.id}"))
                
                await bot.send_message(
                    chat_id=b.client_id,
                    text="✨ <b>Ваш візит завершився!</b>\n\nСподіваємося, вам сподобалось. Будь ласка, залиште короткий відгук про майстра, це допоможе іншим!",
                    reply_markup=kb.as_markup(),
                    parse_mode="HTML"
                )
            except:
                pass
            
            # (Опціонально) Надсилаємо запит майстру
            try:
                kb_m = InlineKeyboardBuilder()
                kb_m.row(InlineKeyboardButton(text="⭐ Відгук про клієнта", callback_data=f"master_review_visit_{b.id}"))
                await bot.send_message(
                    chat_id=b.master_id,
                    text="✨ <b>Візит завершено!</b>\n\nВи можете залишити відгук про клієнта, щоб допомогти іншим майстрам дізнатися більше про нього.",
                    reply_markup=kb_m.as_markup(),
                    parse_mode="HTML"
                )
            except:
                pass
                
        await session.commit()
