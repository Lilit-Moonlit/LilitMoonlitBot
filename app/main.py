import asyncio
import logging
import sys
import io
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage # Пізніше замінимо на Redis
from app.config import BOT_TOKEN
from app.handlers.client import client_router
from app.handlers.master import master_router
from app.handlers.admin import admin_router

# Force UTF-8 encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

async def main():
    print("--- BOT STARTING ---", flush=True)
    logging.basicConfig(level=logging.INFO)
    
    if BOT_TOKEN == "СЮДИ_ВСТАВТЕ_ВАШ_ТОКЕН" or BOT_TOKEN == "PUT_YOUR_TOKEN_HERE":
        print("ERROR: BOT_TOKEN is missing!", flush=True)
        return

    # Ініціалізуємо бота та диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Реєструємо роутери
    dp.include_router(client_router)
    dp.include_router(master_router)
    dp.include_router(admin_router)

    from app.utils.scheduler import setup_scheduler
    setup_scheduler(bot)
    
    # Запускаємо поллінг (постійне опитування серверів Telegram)
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("---" * 10, flush=True)
    print("SUCCESS: Bot is running and ready!", flush=True)
    print("---" * 10, flush=True)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Initializing...", flush=True)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSTOP: Bot stopped by user.", flush=True)
    except Exception as e:
        # Use English for the error message
        print(f"\nCRITICAL ERROR: {e}", flush=True)
