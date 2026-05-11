import asyncio
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Додаємо кореневу директорію бота до шляху пошуку модулів
sys.path.append(str(Path(__file__).parent))

from common.base_bot import FormBot

load_dotenv()

VACANCY_FIELDS = [
    {"key": "position", "prompt": "🏢 Введіть назву посади:"},
    {"key": "company", "prompt": "💼 Введіть назву компанії або роботодавця:"},
    {"key": "salary", "prompt": "💰 Введіть рівень заробітної плати:"},
    {"key": "location", "prompt": "📍 Введіть локацію (місто, район):"},
    {"key": "requirements", "prompt": "📝 Введіть вимоги та обов'язки:"},
    {"key": "contact", "prompt": "📞 Введіть контактні дані (Telegram, телефон тощо):"},
]

async def main():
    token = os.getenv("VACANCY_BOT_TOKEN")
    channel_id = os.getenv("VACANCY_CHANNEL_ID")
    
    if not token or token == "YOUR_VACANCY_BOT_TOKEN":
        print("ERROR: Please set VACANCY_BOT_TOKEN in .env file")
        return

    bot = FormBot(
        token=token,
        channel_id=channel_id,
        bot_type="vacancy",
        fields=VACANCY_FIELDS,
        main_button_text="⬆️Додати оголошення⬆️"
    )
    
    print("Starting Vacancy Bot...")
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
