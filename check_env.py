import sys
import logging

try:
    print("Checking imports...")
    import aiogram
    print(f"Aiogram version: {aiogram.__version__}")
    
    from app.config import BOT_TOKEN, DATABASE_URL
    print(f"BOT_TOKEN found: {BOT_TOKEN[:10]}...")
    print(f"DATABASE_URL: {DATABASE_URL}")
    
    from app.handlers.client import client_router
    print("client_router imported")
    
    print("SUCCESS: All imports okay!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
