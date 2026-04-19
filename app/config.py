import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR")
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql+asyncpg://{os.getenv('DB_USER', 'beauty_bot')}:{os.getenv('DB_PASS', 'bot_password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'beauty_bot_db')}")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
