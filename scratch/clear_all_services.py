import asyncio
from app.database.dal import async_session
from app.database.models import Service, MasterService, Booking
from sqlalchemy import delete

async def clear():
    async with async_session() as s:
        print("Clearing all services and bookings...")
        await s.execute(delete(Booking))
        await s.execute(delete(MasterService))
        await s.execute(delete(Service))
        await s.commit()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(clear())
