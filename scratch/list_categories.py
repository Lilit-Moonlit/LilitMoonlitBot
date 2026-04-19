
import asyncio
import json
from sqlalchemy import select, func
from app.database.models import Service, Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

async def list_categories():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(
            select(Service.category, func.count(Service.id))
            .group_by(Service.category)
        )
        categories = result.all()
        
        # Also let's see some services in those categories
        data = {}
        for cat, count in categories:
            # Get 3 example services for each category
            s_res = await session.execute(
                select(Service.name).where(Service.category == cat).limit(3)
            )
            examples = [r[0] for r in s_res.all()]
            data[cat or "None"] = {
                "count": count,
                "examples": examples
            }
            
        with open("scratch/categories_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    print("Data saved to scratch/categories_data.json")

if __name__ == "__main__":
    asyncio.run(list_categories())
