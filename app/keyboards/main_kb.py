from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Головне меню — точка старту."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔎 Знайти майстра")],
            [KeyboardButton(text="📅 Мої записи")],
            [KeyboardButton(text="💼 Я майстер (Реєстрація)"), KeyboardButton(text="🔄 /start")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Оберіть дію..."
    )

def get_master_menu_keyboard() -> ReplyKeyboardMarkup:
    """Меню майстра з кнопкою повернення до головного меню."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Додати послугу"), KeyboardButton(text="👤 Мій профіль")],
            [KeyboardButton(text="🏠 Головне меню"), KeyboardButton(text="🔄 /start")]
        ],
        resize_keyboard=True
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавіатура скасування активної дії."""
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="❌ Скасувати"),
            KeyboardButton(text="🏠 Головне меню")
        ]],
        resize_keyboard=True
    )

def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Навігаційна клавіатура: крок назад + головне меню."""
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="🔙 Назад"),
            KeyboardButton(text="🏠 Головне меню")
        ]],
        resize_keyboard=True
    )
