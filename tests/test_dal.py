import pytest
from datetime import datetime, timedelta
from app.database import dal
from app.database.models import RoleEnum, BookingStatusEnum

@pytest.mark.asyncio
async def test_create_user():
    user = await dal.create_user(telegram_id=123, name="Test User", role=RoleEnum.CLIENT)
    assert user.telegram_id == 123
    assert user.name == "Test User"
    assert user.role == RoleEnum.CLIENT

@pytest.mark.asyncio
async def test_search_masters_filtering():
    # 1. Створюємо сервіси
    s1 = await dal.get_or_create_service("Манікюр")
    s2 = await dal.get_or_create_service("Педикюр")
    
    # 2. Створюємо майстра з одним сервісом
    await dal.create_user(telegram_id=101, name="Master 1", role=RoleEnum.MASTER)
    await dal.create_master(user_id=101, description="Desc 1")
    await dal.add_master_service(master_id=101, service_id=s1.id, price=500, duration=60)
    
    # 3. Створюємо майстра з двома сервісами
    await dal.create_user(telegram_id=102, name="Master 2", role=RoleEnum.MASTER)
    await dal.create_master(user_id=102, description="Desc 2")
    await dal.add_master_service(master_id=102, service_id=s1.id, price=500, duration=60)
    await dal.add_master_service(master_id=102, service_id=s2.id, price=600, duration=60)
    
    # Тест Match All (обидва сервіси)
    res_all = await dal.get_masters_by_services([s1.id, s2.id], match_all=True)
    assert len(res_all) == 1
    assert res_all[0]["user"].telegram_id == 102
    
    # Тест Match Any (хоча б один)
    res_any = await dal.get_masters_by_services([s1.id, s2.id], match_all=False)
    assert len(res_any) == 2

@pytest.mark.asyncio
async def test_booking_creation_and_confirm():
    user = await dal.create_user(telegram_id=201, name="Client", role=RoleEnum.CLIENT)
    master = await dal.create_user(telegram_id=202, name="Master", role=RoleEnum.MASTER)
    await dal.create_master(user_id=202, description="Desc")
    s1 = await dal.get_or_create_service("Манікюр")
    await dal.add_master_service(master_id=202, service_id=s1.id, price=500, duration=60)
    
    booking = await dal.create_booking(
        client_id=201,
        master_id=202,
        service_id=s1.id,
        start_time="07.04 14:00"
    )
    
    assert booking.client_id == 201
    assert booking.status == BookingStatusEnum.PENDING
    
    # Підтвердження
    await dal.update_booking_status(booking.id, BookingStatusEnum.CONFIRMED)
    updated_booking = await dal.get_booking_by_id(booking.id)
    assert updated_booking.status == BookingStatusEnum.CONFIRMED

@pytest.mark.asyncio
async def test_cancel_booking():
    await dal.create_user(telegram_id=301, name="Client 2", role=RoleEnum.CLIENT)
    await dal.create_user(telegram_id=302, name="Master 2", role=RoleEnum.MASTER)
    await dal.create_master(user_id=302, description="Desc 2")
    s1 = await dal.get_or_create_service("Педикюр")
    await dal.add_master_service(master_id=302, service_id=s1.id, price=700, duration=90)

    booking = await dal.create_booking(
        client_id=301,
        master_id=302,
        service_id=s1.id,
        start_time="07.04 14:00"
    )
    await dal.cancel_booking(booking.id)
    updated = await dal.get_booking_by_id(booking.id)
    assert updated.status == BookingStatusEnum.CANCELLED
