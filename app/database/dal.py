from typing import List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from datetime import datetime
from sqlalchemy import select

from app.config import DATABASE_URL
from app.database.models import User, Master, Service, MasterService, Booking, RoleEnum, BookingStatusEnum, SocialPostQueue, Review, ServiceProposal
from app.catalog import CATALOG_CATEGORY_ORDER, CATALOG_SERVICE_NAMES

# Створення двигуна для БД (SQLite + aiosqlite)
engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_user(telegram_id: int) -> Optional[User]:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()

async def create_user(telegram_id: int, name: str, role: RoleEnum = RoleEnum.CLIENT) -> User:
    async with async_session() as session:
        user = User(telegram_id=telegram_id, name=name, role=role)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def update_user_role(telegram_id: int, role: RoleEnum):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user.scalars().first()
        if user:
            user.role = role
            await session.commit()

async def create_master(user_id: int, description: str, portfolio_url: str = None) -> Master:
    async with async_session() as session:
        # Перевіряємо чи він вже є в базі
        result = await session.execute(select(Master).where(Master.user_id == user_id))
        master = result.scalars().first()
        if not master:
            master = Master(user_id=user_id, description=description, portfolio_url=portfolio_url)
            session.add(master)
        else:
            master.description = description
            if portfolio_url:
                master.portfolio_url = portfolio_url
        await session.commit()
        await session.refresh(master)
        return master

async def get_master(user_id: int) -> Optional[Master]:
    async with async_session() as session:
        result = await session.execute(select(Master).where(Master.user_id == user_id))
        return result.scalars().first()
async def get_or_create_service(name: str) -> Service:
    async with async_session() as session:
        result = await session.execute(select(Service).where(Service.name == name))
        service = result.scalars().first()
        if not service:
            service = Service(name=name)
            session.add(service)
            await session.commit()
            await session.refresh(service)
        return service

async def add_master_service(master_id: int, service_id: int, price: int, duration: int) -> MasterService:
    async with async_session() as session:
        # Upsert: якщо майстер вже має цю послугу - оновлюємо ціну
        existing = await session.execute(
            select(MasterService).where(
                MasterService.master_id == master_id,
                MasterService.service_id == service_id
            )
        )
        master_service = existing.scalars().first()
        if master_service:
            master_service.price = price
            master_service.duration = duration
        else:
            master_service = MasterService(
                master_id=master_id,
                service_id=service_id,
                price=price,
                duration=duration
            )
            session.add(master_service)
        await session.commit()
        await session.refresh(master_service)
        return master_service

async def set_master_services(master_id: int, prices_dict: dict):
    """
    Повністю оновлює список послуг майстра: видаляє старі та додає нові.
    prices_dict: {service_id_str: price_int}
    """
    async with async_session() as session:
        # 1. Видаляємо всі існуючі послуги майстра
        from sqlalchemy import delete
        await session.execute(
            delete(MasterService).where(MasterService.master_id == master_id)
        )
        
        # 2. Додаємо нові
        for sid_str, price in prices_dict.items():
            ms = MasterService(
                master_id=master_id,
                service_id=int(sid_str),
                price=price,
                duration=60 # За замовчуванням 60 хв
            )
            session.add(ms)
        
        await session.commit()

async def get_client_bookings(client_id: int) -> List[Booking]:
    async with async_session() as session:
        # Показуємо очікувані, підтверджені та останні завершені (для відгуків)
        result = await session.execute(
            select(Booking).where(
                Booking.client_id == client_id,
                Booking.status.in_([BookingStatusEnum.PENDING, BookingStatusEnum.CONFIRMED, BookingStatusEnum.COMPLETED])
            ).order_by(Booking.start_time.desc()).limit(10) # 10 останніх
        )
        return result.scalars().all()

async def get_booking_by_id(booking_id: int) -> Optional[Booking]:
    async with async_session() as session:
        result = await session.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalars().first()

async def get_booking_full_details(booking_id: int):
    """Повертає (Booking, ClientUser, MasterUser, MasterProfile, ServiceName)."""
    async with async_session() as session:
        query = (
            select(Booking, User, Master)
            .join(User, User.telegram_id == Booking.client_id)
            .join(Master, Master.user_id == Booking.master_id)
            .where(Booking.id == booking_id)
        )
        result = await session.execute(query)
        row = result.first()
        if not row:
            return None
        
        booking, client, master_prof = row
        
        # Окремо витягуємо User для майстра (бо Master.user_id посилається на User.telegram_id)
        master_user_q = await session.execute(select(User).where(User.telegram_id == master_prof.user_id))
        master_user = master_user_q.scalars().first()
        
        # Витягуємо назву послуги
        service_q = await session.execute(
            select(Service.name)
            .join(MasterService, MasterService.service_id == Service.id)
            .where(MasterService.id == booking.master_service_id)
        )
        service_name = service_q.scalar() or "Послуга"
        
        return {
            "booking": booking,
            "client": client,
            "master_user": master_user,
            "master_profile": master_prof,
            "service_name": service_name
        }

async def cancel_booking(booking_id: int):
    async with async_session() as session:
        result = await session.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalars().first()
        if booking:
            booking.status = BookingStatusEnum.CANCELLED
            await session.commit()

async def update_booking_status(booking_id: int, status: BookingStatusEnum):
    async with async_session() as session:
        result = await session.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalars().first()
        if booking:
            booking.status = status
            await session.commit()

async def add_booking_review(booking_id: int, reviewer_role: RoleEnum, rating: int, comment: str):
    async with async_session() as session:
        # Створюємо відгук
        review = Review(
            booking_id=booking_id,
            reviewer_role=reviewer_role,
            rating=rating,
            comment=comment
        )
        session.add(review)
        
        # Позначаємо в букінгу, що відгук залишено
        result = await session.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalars().first()
        if booking:
            if reviewer_role == RoleEnum.CLIENT:
                booking.is_reviewed_by_client = True
                
                # Оновлюємо загальний рейтинг майстра
                from sqlalchemy import func
                avg_rating = await session.execute(
                    select(func.avg(Review.rating))
                    .join(Booking, Booking.id == Review.booking_id)
                    .where(Booking.master_id == booking.master_id)
                    .where(Review.reviewer_role == RoleEnum.CLIENT)
                )
                new_rating = avg_rating.scalar() or 0.0
                
                master_result = await session.execute(select(Master).where(Master.user_id == booking.master_id))
                master = master_result.scalars().first()
                if master:
                    master.rating = round(new_rating, 2)
                    
            else:
                booking.is_reviewed_by_master = True
        
        await session.commit()

async def get_master_reviews(master_id: int, limit: int = None) -> List:
    """Повертає список відгуків майстра (від найновіших)."""
    async with async_session() as session:
        query = (
            select(Review, User.name)
            .join(Booking, Booking.id == Review.booking_id)
            .join(User, User.telegram_id == Booking.client_id)
            .where(Booking.master_id == master_id)
            .where(Review.reviewer_role == RoleEnum.CLIENT)
            .order_by(Review.created_at.desc())
        )
        if limit:
            query = query.limit(limit)
            
        result = await session.execute(query)
        return result.all()

async def get_reviews_count(master_id: int) -> int:
    """Повертає загальну кількість відгуків клієнтів про майстра."""
    async with async_session() as session:
        from sqlalchemy import func
        query = (
            select(func.count(Review.id))
            .join(Booking, Booking.id == Review.booking_id)
            .where(Booking.master_id == master_id)
            .where(Review.reviewer_role == RoleEnum.CLIENT)
        )
        result = await session.execute(query)
        return result.scalar() or 0

async def get_all_services() -> List[Service]:
    async with async_session() as session:
        result = await session.execute(select(Service))
        services = [s for s in result.scalars().all() if s.category in CATALOG_CATEGORY_ORDER]
        order_map = {cat: i for i, cat in enumerate(CATALOG_CATEGORY_ORDER)}
        return sorted(services, key=lambda s: (order_map.get(s.category, 999), s.name))

async def get_service_by_id(service_id: int) -> Optional[Service]:
    async with async_session() as session:
        result = await session.execute(select(Service).where(Service.id == service_id))
        return result.scalars().first()

async def get_master_service_ids(master_id: int) -> set:
    """Повертає set(service_id) для вказаного майстра (безпечний async варіант)."""
    async with async_session() as session:
        result = await session.execute(
            select(MasterService.service_id).where(MasterService.master_id == master_id)
        )
        return set(result.scalars().all())

async def get_master_services_full(master_id: int) -> List[dict]:
    """Повертає список послуг майстра з назвами та цінами."""
    async with async_session() as session:
        query = (
            select(Service.name, MasterService.price)
            .join(MasterService, MasterService.service_id == Service.id)
            .where(MasterService.master_id == master_id)
        )
        result = await session.execute(query)
        return [{"name": name, "price": price} for name, price in result.all()]

async def get_master_services_prices(master_id: int) -> dict:
    """Повертає {service_id_str: price} для існуючих послуг майстра."""
    async with async_session() as session:
        result = await session.execute(
            select(MasterService.service_id, MasterService.price)
            .where(MasterService.master_id == master_id)
        )
        return {str(svc_id): price for svc_id, price in result.all()}

async def master_has_services(master_id: int) -> bool:
    """Повертає True якщо майстер має хоча б одну послугу."""
    async with async_session() as session:
        result = await session.execute(
            select(MasterService.id).where(MasterService.master_id == master_id).limit(1)
        )
        return result.scalars().first() is not None

async def get_masters_by_services(service_ids: List[int], match_all: bool = True) -> List[dict]:
    service_ids = [int(sid) for sid in service_ids]
    print(f"[DEBUG] Searching for Master with services: {service_ids} (match_all={match_all})")

    async with async_session() as session:
        # Крок 1: Знаходимо майстрів, які надають обрані послуги
        query = (
            select(Master, User, MasterService, Service)
            .join(User, User.telegram_id == Master.user_id)
            .join(MasterService, Master.user_id == MasterService.master_id)
            .join(Service, Service.id == MasterService.service_id)
            .where(MasterService.service_id.in_(service_ids))
        )
        result = await session.execute(query)
        rows = result.all()

        # Групуємо по майстрах
        masters_map = {}
        for master, user, master_service, service in rows:
            if master.user_id not in masters_map:
                masters_map[master.user_id] = {
                    "master": master,
                    "user": user,
                    "matched_services": [],  # послуги, що відповідають пошуку
                    "all_services": []        # всі послуги майстра (заповнимо нижче)
                }
            masters_map[master.user_id]["matched_services"].append({
                "service_name": service.name,
                "service_id": service.id,
                "price": master_service.price
            })

        # Фільтрація по match_all
        final_ids = []
        for uid, data in masters_map.items():
            found_ids = {s["service_id"] for s in data["matched_services"]}
            if match_all:
                if set(service_ids).issubset(found_ids):
                    final_ids.append(uid)
            else:
                final_ids.append(uid)

        if not final_ids:
            return []

        # Крок 2: Завантажуємо ВСІ послуги кожного знайденого майстра
        all_svcs_query = (
            select(MasterService, Service)
            .join(Service, Service.id == MasterService.service_id)
            .where(MasterService.master_id.in_(final_ids))
        )
        all_svcs_result = await session.execute(all_svcs_query)
        all_svcs_rows = all_svcs_result.all()

        all_svcs_map: dict = {}
        for ms, srv in all_svcs_rows:
            all_svcs_map.setdefault(ms.master_id, []).append({
                "service_name": srv.name,
                "service_id": srv.id,
                "price": ms.price
            })

        # Збираємо фінальний список
        final_list = []
        for uid in final_ids:
            data = masters_map[uid]
            data["all_services"] = all_svcs_map.get(uid, [])
            final_list.append(data)

        print(f"[DEBUG] Found {len(final_list)} masters matching criteria.")
        return final_list

async def create_booking(client_id: int, master_id: int, service_id: int, start_time: datetime | str, comment: str = None) -> Booking:
    async with async_session() as session:
        if isinstance(start_time, str):
            from app.utils.time_parser import parse_datetime_flexible
            start_time = parse_datetime_flexible(start_time)

        # Шукаємо реальний ID послуги цього майстра (MasterService)
        # бо в таблиці bookings ми зберігаємо саме master_service_id
        ms_query = select(MasterService).where(MasterService.master_id == master_id).where(
            (MasterService.service_id == service_id) | (MasterService.id == service_id)
        )
        ms_result = await session.execute(ms_query)
        master_service = ms_result.scalars().first()
        
        if not master_service:
            # Фолбек: якщо не знайшли точну послугу (маловірогідно), беремо першу ліпшу цього майстра
            ms_fallback_q = select(MasterService).where(MasterService.master_id == master_id)
            ms_fallback = await session.execute(ms_fallback_q)
            master_service = ms_fallback.scalars().first()
        
        if not master_service:
            raise ValueError(f"Master {master_id} has no services.")

        duration = master_service.duration or 60
        from datetime import timedelta
        end_time = start_time + timedelta(minutes=duration)

        booking = Booking(
            client_id=client_id,
            master_id=master_id,
            master_service_id=master_service.id,
            start_time=start_time,
            end_time=end_time,
            status=BookingStatusEnum.PENDING,
            comment=comment
        )
        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        return booking

async def confirm_booking_with_time(booking_id: int, start_time_str: str):
    from app.utils.time_parser import parse_datetime_flexible
    try:
        dt = parse_datetime_flexible(start_time_str)
    except ValueError:
        from datetime import datetime
        dt = datetime.now()

    async with async_session() as session:
        result = await session.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalars().first()
        if booking:
            booking.start_time = dt
            booking.end_time = dt
            booking.status = BookingStatusEnum.CONFIRMED
            await session.commit()

async def propose_booking_with_time(booking_id: int, start_time_str: str):
    from app.utils.time_parser import parse_datetime_flexible
    try:
        dt = parse_datetime_flexible(start_time_str)
    except ValueError:
        from datetime import datetime
        dt = datetime.now()

    async with async_session() as session:
        result = await session.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalars().first()
        if booking:
            booking.start_time = dt
            booking.end_time = dt
            booking.status = BookingStatusEnum.PROPOSED
            await session.commit()

async def update_master_profile(user_id: int, **kwargs):
    async with async_session() as session:
        result = await session.execute(select(Master).where(Master.user_id == user_id))
        master = result.scalars().first()
        if master:
            for key, value in kwargs.items():
                if hasattr(master, key):
                    setattr(master, key, value)
            await session.commit()

async def create_service_proposal(master_id: int, service_name: str, category_name: str = None):
    async with async_session() as session:
        proposal = ServiceProposal(
            master_id=master_id,
            service_name=service_name,
            category_name=category_name
        )
        session.add(proposal)
        await session.commit()
        return proposal

async def get_pending_proposals():
    async with async_session() as session:
        result = await session.execute(select(ServiceProposal).where(ServiceProposal.status == "pending"))
        return result.scalars().all()

async def approve_service_proposal(proposal_id: int):
    async with async_session() as session:
        result = await session.execute(select(ServiceProposal).where(ServiceProposal.id == proposal_id))
        proposal = result.scalars().first()
        if proposal:
            proposal.status = "approved"
            # Створюємо саму послугу
            service = Service(name=proposal.service_name, category=proposal.category_name)
            session.add(service)
            await session.commit()
            await session.refresh(service)
            return service

async def add_to_post_queue(ad_type: str, text: str, media_file_id: str = None, media_type: str = None):
    async with async_session() as session:
        post = SocialPostQueue(
            ad_type=ad_type,
            text=text,
            media_file_id=media_file_id,
            media_type=media_type,
            status="pending"
        )
        session.add(post)
        await session.commit()
        return post

async def get_next_queued_post() -> Optional[SocialPostQueue]:
    async with async_session() as session:
        result = await session.execute(
            select(SocialPostQueue)
            .where(SocialPostQueue.status == "pending")
            .order_by(SocialPostQueue.created_at.asc())
            .limit(1)
        )
        return result.scalars().first()

async def update_queued_post_status(post_id: int, status: str, error_message: str = None):
    async with async_session() as session:
        result = await session.execute(select(SocialPostQueue).where(SocialPostQueue.id == post_id))
        post = result.scalars().first()
        if post:
            post.status = status
            post.error_message = error_message
            post.processed_at = datetime.utcnow()
            await session.commit()
