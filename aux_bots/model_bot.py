import asyncio
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Додаємо кореневу директорію бота до шляху пошуку модулів
sys.path.append(str(Path(__file__).parent))

from common.base_bot import FormBot

load_dotenv()

MODEL_FIELDS = [
    {"key": "service", "prompt": "💅 Введіть назву послуги (напр. манікюр, брови):"},
    {"key": "datetime", "prompt": "📅 Введіть бажану дату та час:"},
    {"key": "location", "prompt": "📍 Введіть локацію (студія, район):"},
    {"key": "requirements", "prompt": "📝 Введіть вимоги до моделі (напр. чиста шкіра, довге волосся):"},
    {"key": "price", "prompt": "💵 Введіть вартість (або напишіть 'Безкоштовно'):"},
    {"key": "contact", "prompt": "📞 Введіть ваші контактні дані:"},
]

async def main():
    token = os.getenv("MODEL_BOT_TOKEN")
    channel_id = os.getenv("MODEL_CHANNEL_ID")
    
    if not token or token == "YOUR_MODEL_BOT_TOKEN":
        print("ERROR: Please set MODEL_BOT_TOKEN in .env file")
        return

    bot = FormBot(
        token=token,
        channel_id=channel_id,
        bot_type="model",
        fields=MODEL_FIELDS,
        main_button_text="⬆️Додати оголошення⬆️"
    )
    
    print("Starting Model Bot...")
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
