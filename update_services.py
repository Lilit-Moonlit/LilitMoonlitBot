import asyncio

from sqlalchemy import select

from app.catalog import SERVICE_CATALOG
from app.database.dal import async_session
from app.database.models import Service


async def sync_services_catalog() -> None:
    created = 0
    updated = 0

    async with async_session() as session:
        for category, service_names in SERVICE_CATALOG.items():
            for service_name in service_names:
                query = await session.execute(
                    select(Service).where(
                        Service.name == service_name,
                        Service.category == category
                    )
                )
                service = query.scalars().first()

                if not service:
                    service = Service(name=service_name, category=category)
                    session.add(service)
                    created += 1

        await session.commit()

    total = sum(len(names) for names in SERVICE_CATALOG.values())
    print("Service catalog sync complete")
    print(f"Canonical items: {total}")
    print(f"Created: {created}")
    print(f"Updated category: {updated}")


if __name__ == "__main__":
    asyncio.run(sync_services_catalog())
