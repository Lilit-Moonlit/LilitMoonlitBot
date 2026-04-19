import enum
from datetime import datetime
from sqlalchemy import BigInteger, Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class RoleEnum(str, enum.Enum):
    CLIENT = "client"
    MASTER = "master"
    ADMIN = "admin"

class BookingStatusEnum(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PROPOSED = "proposed"

class User(Base):
    __tablename__ = 'users'

    telegram_id = Column(BigInteger, primary_key=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.CLIENT, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    city = Column(String(50), default="Одеса")
    language = Column(String(10), default="uk")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    master_profile = relationship("Master", back_populates="user", uselist=False, cascade="all, delete-orphan")
    client_bookings = relationship("Booking", back_populates="client", cascade="all, delete-orphan")

class Master(Base):
    __tablename__ = 'masters'

    user_id = Column(BigInteger, ForeignKey('users.telegram_id', ondelete='CASCADE'), primary_key=True)
    description = Column(Text, nullable=True)
    portfolio_url = Column(String(255), nullable=True) # Посилання на Instagram або Telegram канал
    rating = Column(Numeric(3, 2), default=0.0) # Рейтинг
    is_active = Column(Boolean, default=True)
    
    # Нові соціальні мережі
    instagram = Column(String(100), nullable=True)
    facebook = Column(String(100), nullable=True)
    tiktok = Column(String(100), nullable=True)
    telegram = Column(String(100), nullable=True)
    whatsapp = Column(String(100), nullable=True)
    viber = Column(String(100), nullable=True)
    phone = Column(String(100), nullable=True)
    website = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="master_profile")
    services = relationship("MasterService", back_populates="master", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="master", cascade="all, delete-orphan")

class ServiceProposal(Base):
    __tablename__ = 'service_proposals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    master_id = Column(BigInteger, ForeignKey('masters.user_id', ondelete='CASCADE'), nullable=False)
    service_name = Column(String(100), nullable=False)
    category_name = Column(String(100), nullable=True)
    status = Column(String(20), default="pending") # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True) # наприклад: Манікюр, Вії, Брови

    master_services = relationship("MasterService", back_populates="service", cascade="all, delete-orphan")

class MasterService(Base):
    __tablename__ = 'master_services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    master_id = Column(BigInteger, ForeignKey('masters.user_id', ondelete='CASCADE'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id', ondelete='CASCADE'), nullable=False)
    price = Column(Integer, nullable=False) # Ціна в грн
    duration = Column(Integer, nullable=False) # Тривалість у хвилинах

    # Relationships
    master = relationship("Master", back_populates="services")
    service = relationship("Service", back_populates="master_services")
    bookings = relationship("Booking", back_populates="master_service")

class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(BigInteger, ForeignKey('users.telegram_id', ondelete='CASCADE'), nullable=False)
    master_id = Column(BigInteger, ForeignKey('masters.user_id', ondelete='CASCADE'), nullable=False)
    master_service_id = Column(Integer, ForeignKey('master_services.id', ondelete='CASCADE'), nullable=False)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatusEnum), default=BookingStatusEnum.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    is_reviewed_by_client = Column(Boolean, default=False)
    is_reviewed_by_master = Column(Boolean, default=False)
    is_reminder_sent = Column(Boolean, default=False)
    comment = Column(Text, nullable=True) # Коментар клієнта (для послуги "Інше")

    # Relationships
    client = relationship("User", back_populates="client_bookings")
    master = relationship("Master", back_populates="bookings")
    master_service = relationship("MasterService", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False, cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False)
    reviewer_role = Column(Enum(RoleEnum), nullable=False) # Хто залишив: CLIENT або MASTER
    rating = Column(Integer, nullable=False) # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    booking = relationship("Booking", back_populates="review")
