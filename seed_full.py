import asyncio
import random
from app.database.dal import async_session, engine
from app.database.models import Base, User, Master, Service, MasterService, RoleEnum
from sqlalchemy import select

async def seed_data():
    # 0. Створюємо таблиці (для SQLite це важливо при першому запуску)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as session:
        # 1. Створюємо 40 послуг
        service_data = [
            # Нігті
            ("Манікюр з покриттям", "Нігті"), ("Апаратний педикюр", "Нігті"), 
            ("Нарощування нігтів", "Нігті"), ("Дизайн нігтів", "Нігті"),
            ("Зняття гель-лаку", "Нігті"), ("СПА-манікюр", "Нігті"),
            # Волосся
            ("Стрижка жіноча", "Волосся"), ("Стрижка чоловіча", "Волосся"),
            ("Фарбування (Airtouch)", "Волосся"), ("Кератинове вирівнювання", "Волосся"),
            ("Укладка волосся", "Волосся"), ("Ботокс для волосся", "Волосся"),
            ("Мелірування", "Волосся"), ("Тонування волосся", "Волосся"),
            # Вії та брови (Вії/Брови/Макіяж)
            ("Ламінування вій", "Вії та брови"), ("Нарощування вій (2D)", "Вії та брови"), 
            ("Корекція брів", "Вії та брови"), ("Фарбування брів (хна)", "Вії та брови"),
            ("Денний макіяж", "Вії та брови"), ("Вечірній макіяж", "Вії та брови"),
            ("Перманентний макіяж губ", "Вії та брови"), ("Пудрове напилення брів", "Вії та брови"),
            # Тіло
            ("Масаж класичний", "Тіло"), ("Антицелюлітний масаж", "Тіло"),
            ("Лімфодренажний масаж", "Тіло"), ("Масаж спини", "Тіло"),
            ("Лазерна епіляція (ноги)", "Тіло"), ("Шугаринг (бікіні)", "Тіло"),
            ("Воскова депіляція", "Тіло"), ("Обгортання тіла", "Тіло"),
            # Косметологія
            ("Чистка обличчя (ультразвук)", "Косметологія"), ("Пілінг", "Косметологія"),
            ("Мезотерапія", "Косметологія"), ("Маска для обличчя", "Косметологія"),
            ("Масаж обличчя", "Косметологія"), ("Карбокситерапія", "Косметологія"),
            # Інше
            ("Прокол вух", "Інше"), ("Татуювання (міні)", "Інше"),
            ("Весільний образ", "Інше"), ("Консультація стиліста", "Інше")
        ]
        
        db_services = []
        for name, cat in service_data:
            s_q = await session.execute(select(Service).where(Service.name == name))
            service = s_q.scalars().first()
            if not service:
                service = Service(name=name, category=cat)
                session.add(service)
            db_services.append(service)
        
        await session.commit()
        # Повторно витягуємо послуги, щоб мати актуальні ID
        s_q = await session.execute(select(Service))
        db_services = s_q.scalars().all()

        # 2. Створюємо 40 майстрів
        names = [
            "Анна", "Марія", "Олена", "Вікторія", "Юлія", "Наталія", "Ольга", "Тетяна", 
            "Анастасія", "Ірина", "Світлана", "Оксана", "Інна", "Людмила", "Катерина", "Аліна",
            "Діана", "Христина", "Софія", "Яна", "Ангеліна", "Вероніка", "Дарина", "Марта",
            "Аліса", "Єлизавета", "Таїсія", "Злата", "Олександра", "Поліна", "Валентина", "Галина",
            "Надія", "Любов", "Тамаpа", "Раїса", "Павло", "Артем", "Максим", "Денис"
        ]
        
        for i in range(40):
            telegram_id = 1000000 + i # Фейкові ID
            name = names[i] if i < len(names) else f"Майстер {i+1}"
            
            # Створюємо User
            u_q = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = u_q.scalars().first()
            if not user:
                user = User(telegram_id=telegram_id, name=name, role=RoleEnum.MASTER)
                session.add(user)
                await session.commit()
            
            # Створюємо Master
            m_q = await session.execute(select(Master).where(Master.user_id == telegram_id))
            master = m_q.scalars().first()
            if not master:
                master = Master(
                    user_id=telegram_id, 
                    description=f"Професійний сервіс від {name}. Досвід роботи понад {random.randint(1, 10)} років.",
                    portfolio_url=f"https://instagram.com/master_{i+1}"
                )
                session.add(master)
                await session.commit()

            # Призначаємо від 3 до 15 випадкових послуг
            num_services = random.randint(3, 15)
            assigned_services = random.sample(db_services, num_services)
            
            for s in assigned_services:
                # Перевіряємо чи вже є така послуга у майстра
                ms_q = await session.execute(
                    select(MasterService)
                    .where(MasterService.master_id == telegram_id)
                    .where(MasterService.service_id == s.id)
                )
                if not ms_q.scalars().first():
                    ms = MasterService(
                        master_id=telegram_id,
                        service_id=s.id,
                        price=random.randint(200, 2000) // 10 * 10, # Округляємо до 10 грн
                        duration=random.choice([30, 60, 90, 120])
                    )
                    session.add(ms)
        
        await session.commit()
        print(f"Database seeded successfully with {len(db_services)} services and 40 masters.")

if __name__ == "__main__":
    asyncio.run(seed_data())
