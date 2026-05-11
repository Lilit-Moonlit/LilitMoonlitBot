from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Скасувати")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_main_menu_kb(button_text="📝 Створити оголошення"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=button_text)],
            [KeyboardButton(text="💎 Наші ресурси"), KeyboardButton(text="✨ Реєстрація/послуги")]
        ],
        resize_keyboard=True
    )

def get_preview_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Опублікувати", callback_data="publish")],
            [InlineKeyboardButton(text="🔄 Заповнити заново", callback_data="restart")],
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel")]
        ]
    )

def get_channel_post_kb(bot_type: str):
    # Determine the bot username based on type
    bot_link = "https://t.me/LilitVacancyBot" if bot_type == "vacancy" else "https://t.me/LilitSearchModelBot"
    button_text = "⬆️Додати оголошення⬆️"
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💎 Наші ресурси", url="https://t.me/LilitSociety")],
            [InlineKeyboardButton(text=button_text, url=bot_link)]
        ]
    )
