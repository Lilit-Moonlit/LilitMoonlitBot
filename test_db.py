import asyncio
from app.database.dal import get_masters_by_services, get_all_services

async def main():
    services = await get_all_services()
    print("Maste Services length:", len(services))
    # Let's try to pass the first service ID
    if not services:
        print("No services in DB!")
        return
        
    for s in services:
        res = await get_masters_by_services([s.id], match_all=False)
        print(f"Service {s.id} Result length: {len(res)}")

if __name__ == "__main__":
    asyncio.run(main())
