
import asyncio
import json
from sqlalchemy import select
from app.database.models import Service
from app.database.dal import async_session

async def list_all_services():
    async with async_session() as session:
        result = await session.execute(select(Service.category, Service.name))
        services = result.all()
        
        data = {}
        for cat, name in services:
            cat_name = cat or "None"
            if cat_name not in data:
                data[cat_name] = []
            data[cat_name].append(name)
            
        with open("scratch/all_services.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(list_all_services())
