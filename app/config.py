import os
from dotenv import load_dotenv

load_dotenv()

# --- Bot Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")
ADMIN_USERNAMES = os.getenv("ADMIN_USERNAMES", "denisbelii").split(",")

# --- Database Configuration ---
# Example for SQLite: sqlite+aiosqlite:///beauty_bot.db
# Example for Postgres: postgresql+asyncpg://user:pass@host:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///beauty_bot.db")

# --- Redis Configuration (High Load) ---
USE_REDIS = os.getenv("USE_REDIS", "False").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# --- Ads Configuration ---
VACANCY_CHANNEL_ID = os.getenv("VACANCY_CHANNEL_ID")
MODEL_CHANNEL_ID = os.getenv("MODEL_CHANNEL_ID")

# --- Meta API (Cross-Posting) ---
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
# Моделі
FB_PAGE_ID_MODELS = os.getenv("FB_PAGE_ID_MODELS")
IG_BUSINESS_ACCOUNT_ID_MODELS = os.getenv("IG_BUSINESS_ACCOUNT_ID_MODELS")
# Вакансії
FB_PAGE_ID_VACANCIES = os.getenv("FB_PAGE_ID_VACANCIES")
IG_BUSINESS_ACCOUNT_ID_VACANCIES = os.getenv("IG_BUSINESS_ACCOUNT_ID_VACANCIES")
ENABLE_SOCIAL_POSTING = os.getenv("ENABLE_SOCIAL_POSTING", "False").lower() == "true"
