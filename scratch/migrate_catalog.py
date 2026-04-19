import asyncio
from app.database.dal import async_session
from app.database.models import MasterService, Service, Booking, Review
from sqlalchemy import delete

async def purge_and_migrate():
    async with async_session() as session:
        # 1. Delete reviews, bookings to prevent FK issues
        print("Deleting reviews...")
        await session.execute(delete(Review))
        print("Deleting bookings...")
        await session.execute(delete(Booking))
        print("Deleting master_services...")
        await session.execute(delete(MasterService))
        print("Deleting services...")
        await session.execute(delete(Service))
        
        await session.commit()
    print("Database purged of test service dependencies.")

if __name__ == "__main__":
    asyncio.run(purge_and_migrate())
