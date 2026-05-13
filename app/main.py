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
from app.handlers.ads import ads_router

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

def run_migrations():
    from alembic.config import Config
    from alembic import command
    print("--- INFO: Running automatic database migrations ---", flush=True)
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("--- SUCCESS: Migrations applied successfully ---", flush=True)
    except Exception as e:
        print(f"--- WARNING: Migrations failed: {e} ---", flush=True)

async def main():
    run_migrations()
    print("--- BOT STARTING ---", flush=True)
    logging.basicConfig(level=logging.INFO)
    
    if BOT_TOKEN == "СЮДИ_ВСТАВТЕ_ВАШ_ТОКЕН" or BOT_TOKEN == "PUT_YOUR_TOKEN_HERE":
        print("ERROR: BOT_TOKEN is missing!", flush=True)
        return

    # Ініціалізуємо бота та диспетчер
    bot = Bot(token=BOT_TOKEN)
    
    from app.config import USE_REDIS, REDIS_URL
    if USE_REDIS:
        from aiogram.fsm.storage.redis import RedisStorage
        storage = RedisStorage.from_url(REDIS_URL)
        print(f"--- INFO: Using Redis Storage ({REDIS_URL}) ---", flush=True)
    else:
        storage = MemoryStorage()
        print("--- INFO: Using Memory Storage ---", flush=True)
        
    dp = Dispatcher(storage=storage)
    
    # Реєструємо роутери
    dp.include_router(client_router)
    dp.include_router(master_router)
    dp.include_router(admin_router)
    dp.include_router(ads_router)
    
    # Реєструємо Middleware
    from app.middlewares.album import AlbumMiddleware
    from app.middlewares.antiflood import AntiFloodMiddleware
    
    # 1. Спочатку збираємо альбоми
    dp.message.middleware(AlbumMiddleware(latency=0.2))
    
    # 2. Потім перевіряємо на Anti-Flood (тільки для кнопок/тексту)
    dp.message.middleware(AntiFloodMiddleware(limit=0.7))
    dp.callback_query.middleware(AntiFloodMiddleware(limit=0.7))

    from app.utils.scheduler import setup_scheduler
    setup_scheduler(bot)
    
    # Запускаємо веб-сервер для Health Check (потрібно для Render)
    from aiohttp import web
    async def handle_health_check(request):
        return web.Response(text="OK")

    app = web.Application()
    app.router.add_get("/", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render передає порт через змінну оточення PORT
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"--- INFO: Health check server started on port {port} ---", flush=True)

    # Запускаємо поллінг (постійне опитування серверів Telegram)
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("---" * 10, flush=True)
    print("SUCCESS: Bot is running and ready!", flush=True)
    print("---" * 10, flush=True)
    
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    import os
    print("Initializing...", flush=True)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSTOP: Bot stopped by user.", flush=True)
    except Exception as e:
        # Use English for the error message
        print(f"\nCRITICAL ERROR: {e}", flush=True)
