import asyncio
import logging
import os
from typing import List, Dict, Any

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from .keyboards import get_cancel_kb, get_preview_kb, get_main_menu_kb, get_channel_post_kb
from .templates import format_post

ECOSYSTEM_TEXT = (
    "Вітаю у <b>Lili⚸ Ecosystem</b>! 👋\n\n"
    "Я допоможу вам створити пост для каналу.\n\n"
    "💎 <b>Наші ресурси:</b>\n"
    "• @LilitMoonlitBot — послуги/зареєстрація\n"
    "• https://t.me/LilitModel — шукають модель\n"
    "• @LilitSearchModelBot — знайти модель\n"
    "• https://t.me/LilitVacancy — вакансії\n"
    "• @LilitVacancyBot — додати вакансію\n"
    "• https://t.me/LilitSociety — спільнота"
)

class FormBot:
    def __init__(self, token: str, channel_id: str, bot_type: str, fields: List[Dict[str, str]], main_button_text: str):
        self.token = token
        self.channel_id = channel_id
        self.bot_type = bot_type
        self.fields = fields
        self.main_button_text = main_button_text
        
        self.bot = Bot(token=token, parse_mode="HTML")
        self.dp = Dispatcher(storage=MemoryStorage())
        self.router = Router()
        
        # Define states dynamically
        class FormStates(StatesGroup):
            filling = State()
            preview = State()
            
        self.States = FormStates
        self.setup_handlers()
        self.dp.include_router(self.router)

    def setup_handlers(self):
        @self.router.message(Command("start"))
        async def cmd_start(message: Message, state: FSMContext):
            await state.clear()
            await message.answer(ECOSYSTEM_TEXT, reply_markup=get_main_menu_kb(self.main_button_text))

        @self.router.message(lambda m: m.text == self.main_button_text)
        async def start_form(message: Message, state: FSMContext):
            await state.clear()
            await message.answer("Починаємо заповнення форми. Ви можете скасувати процес у будь-який момент кнопкою нижче.", reply_markup=get_cancel_kb())
            
            # Start the first field
            first_field = self.fields[0]
            await message.answer(first_field["prompt"])
            await state.set_state(self.States.filling)
            await state.update_data(current_field_idx=0)

        @self.router.message(F.text == "💎 Наші ресурси")
        async def community_button(message: Message):
            await message.answer(ECOSYSTEM_TEXT)

        @self.router.message(F.text == "✨ Реєстрація/послуги")
        async def main_bot_button(message: Message):
            await message.answer("Наш головний бот для запису до майстрів та реєстрації: @LilitMoonlitBot")

        @self.router.message(F.text == "❌ Скасувати")
        async def cancel_handler(message: Message, state: FSMContext):
            await state.clear()
            await message.answer("Процес скасовано.", reply_markup=get_main_menu_kb(self.main_button_text))

        @self.router.message(self.States.filling)
        async def process_field(message: Message, state: FSMContext):
            data = await state.get_data()
            idx = data.get("current_field_idx", 0)
            
            # Save current field value
            field_key = self.fields[idx]["key"]
            await state.update_data({field_key: message.text})
            
            # Move to next field or preview
            next_idx = idx + 1
            if next_idx < len(self.fields):
                await state.update_data(current_field_idx=next_idx)
                await message.answer(self.fields[next_idx]["prompt"])
            else:
                # All fields filled, show preview
                all_data = await state.get_data()
                preview_text = format_post(all_data, self.bot_type)
                
                await message.answer("👀 <b>Попередній перегляд вашого поста:</b>", reply_markup=get_main_menu_kb(self.main_button_text))
                await message.answer(preview_text, reply_markup=get_preview_kb())
                await state.set_state(self.States.preview)

        @self.router.callback_query(F.data == "publish", self.States.preview)
        async def cmd_publish(callback: CallbackQuery, state: FSMContext):
            all_data = await state.get_data()
            post_text = format_post(all_data, self.bot_type)
            
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id, 
                    text=post_text, 
                    reply_markup=get_channel_post_kb(self.bot_type)
                )
                await callback.message.edit_text("✅ <b>Успішно опубліковано у каналі!</b>")
                await state.clear()
            except Exception as e:
                logging.error(f"Error publishing: {e}")
                await callback.message.answer(f"❌ Помилка при публікації: {e}")

        @self.router.callback_query(F.data == "restart", self.States.preview)
        async def cmd_restart(callback: CallbackQuery, state: FSMContext):
            await callback.answer("Починаємо спочатку")
            await cmd_start(callback.message, state)

        @self.router.callback_query(F.data == "cancel", self.States.preview)
        async def cmd_cancel_callback(callback: CallbackQuery, state: FSMContext):
            await state.clear()
            await callback.message.edit_text("❌ Процес скасовано.")

    async def run(self):
        logging.basicConfig(level=logging.INFO)
        await self.dp.start_polling(self.bot)
