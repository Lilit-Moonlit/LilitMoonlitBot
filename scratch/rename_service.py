import asyncio
from sqlalchemy import update
from app.database.dal import async_session
from app.database.models import Service

async def rename():
    async with async_session() as session:
        await session.execute(update(Service).where(Service.name == 'Прокол вух').values(name='Пірсінг'))
        await session.commit()
    print('Rename complete')

if __name__ == "__main__":
    asyncio.run(rename())
