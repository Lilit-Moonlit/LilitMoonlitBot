import asyncio
import os
import sys

# Додаємо поточну директорію до path, щоб імпортувати app
sys.path.append(os.getcwd())

from app.database import dal

async def check():
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    try:
        services = await dal.get_all_services()
        print(f"Total services found: {len(services)}")
        categories = set(s.category for s in services)
        print(f"Categories in DB: {list(categories)}")
        for s in services:
            print(f"- {s.name} | Cat: {s.category}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
