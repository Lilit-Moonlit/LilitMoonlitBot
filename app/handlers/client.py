import html
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from app.keyboards.main_kb import get_start_keyboard
from app.keyboards.inline import get_services_keyboard
from app.states.booking import ClientBooking
from app.states.review_states import ReviewStates
from app.database import dal
from app.database.models import RoleEnum, BookingStatusEnum

client_router = Router()


def get_skip_comment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Пропустити ⏭️", callback_data="skip_booking_comment"))
    return builder.as_markup()

@client_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await dal.get_user(message.from_user.id)
    
    if not user:
        # Реєструємо як клієнта за замовчуванням
        await dal.create_user(
            telegram_id=message.from_user.id,
            name=message.from_user.first_name,
            role=RoleEnum.CLIENT
        )
    
    text = (
        f"Привіт, {message.from_user.first_name}! 🌸\n\n"
        "Я твій надійний помічник у світі краси.\n"
        "Тут ти можеш знайти найкращого майстра у своєму місті "
        "або зареєструватися як майстер."
    )
    await message.answer(text, reply_markup=get_start_keyboard())

@client_router.message(F.text == "/ping")
async def cmd_ping(message: Message):
    await message.answer("Pong! 🏓 Бот працює!")

# ─── Навігація (найвищий пріоритет) ────────────────────────────────────────
@client_router.message(F.text.in_(["🏠 Головне меню", "Головне меню"]))
async def go_to_main_menu(message: Message, state: FSMContext):
    """Завжди повертає до головного меню, незалежно від стану."""
    await state.clear()
    await message.answer("🏠 Головне меню:", reply_markup=get_start_keyboard())

@client_router.message(F.text.in_(["🔙 Назад", "Назад"]), ClientBooking.waiting_for_match_type)
async def client_back_match_type(message: Message, state: FSMContext):
    """З вибору типу пошуку → назад до каталогу послуг."""
    await state.set_state(ClientBooking.waiting_for_service_selection)
    services = await dal.get_all_services()
    data = await state.get_data()
    selected_services = data.get("selected_services", [])
    from app.keyboards.inline import get_categories_keyboard
    keyboard = get_categories_keyboard(services, set(selected_services))
    from app.keyboards.main_kb import get_back_keyboard
    await message.answer("Повернення до вибору послуг:", reply_markup=get_back_keyboard())
    await message.answer("Каталог послуг. Оберіть категорію:", reply_markup=keyboard)

@client_router.message(F.text.in_(["🔙 Назад", "Назад"]), ClientBooking.waiting_for_service_selection)
@client_router.message(F.text.in_(["🔙 Назад", "Назад"]), ClientBooking.waiting_for_date_time)
@client_router.message(F.text.in_(["🔙 Назад", "Назад"]), ClientBooking.waiting_for_search_wishes)
@client_router.message(F.text.in_(["🔙 Назад", "Назад"]), ClientBooking.waiting_for_negotiation)
@client_router.message(F.text.in_(["🔙 Назад", "Назад"]), ClientBooking.waiting_for_master_response)
@client_router.message(F.text.in_(["🔙 Назад", "Назад"]), ClientBooking.waiting_for_custom_service_description)
async def client_back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Головне меню:", reply_markup=get_start_keyboard())

@client_router.message(F.text == "❌ Скасувати")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Головне меню:", reply_markup=get_start_keyboard())

@client_router.message(F.text.contains("Знайти майстра"))
async def start_find_master(message: Message, state: FSMContext):
    await state.clear() 
    services = await dal.get_all_services()
    if not services:
        await message.answer("На жаль, поки що немає активних послуг.")
        return
        
    await state.set_state(ClientBooking.waiting_for_service_selection)
    await state.update_data(selected_services=[])
    
    from app.keyboards.main_kb import get_back_keyboard
    from app.keyboards.inline import get_categories_keyboard
    await message.answer("Які послуги вас цікавлять? (Можна обрати декілька)", reply_markup=get_back_keyboard())
    
    keyboard = get_categories_keyboard(services, set())
    await message.answer("Каталог послуг. Оберіть категорію:", reply_markup=keyboard)

@client_router.callback_query(F.data.startswith("select_cat_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    # Відновлюємо стан якщо бот перезапустився (MemoryStorage скинув стан)
    current_state = await state.get_state()
    if current_state != ClientBooking.waiting_for_service_selection.state:
        await state.set_state(ClientBooking.waiting_for_service_selection)
        await state.update_data(selected_services=[])

    category = callback.data.replace("select_cat_", "")
    await state.update_data(current_category=category)
    
    services = await dal.get_all_services()
    data = await state.get_data()
    selected_services = data.get("selected_services", [])
    
    from app.keyboards.inline import get_services_keyboard
    keyboard = get_services_keyboard(services, set(selected_services), category)
    
    await callback.message.edit_text(f"📂 <b>Категорія: {category}</b>\nОберіть потрібні послуги:", reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@client_router.callback_query(F.data == "back_to_categories")
async def back_to_categories_callback(callback: CallbackQuery, state: FSMContext):
    # Відновлюємо стан якщо потрібно
    current_state = await state.get_state()
    if current_state != ClientBooking.waiting_for_service_selection.state:
        await state.set_state(ClientBooking.waiting_for_service_selection)
        await state.update_data(selected_services=[])

    services = await dal.get_all_services()
    data = await state.get_data()
    selected_services = data.get("selected_services", [])
    
    from app.keyboards.inline import get_categories_keyboard
    keyboard = get_categories_keyboard(services, set(selected_services))
    
    await callback.message.edit_text("Каталог послуг. Оберіть категорію:", reply_markup=keyboard)
    await callback.answer()

@client_router.callback_query(F.data.startswith("serv_"))
async def process_service_selection(callback: CallbackQuery, state: FSMContext):
    # Відновлюємо стан якщо потрібно
    current_state = await state.get_state()
    if current_state != ClientBooking.waiting_for_service_selection.state:
        await state.set_state(ClientBooking.waiting_for_service_selection)

    service_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    selected_services = data.get("selected_services", [])
    current_category = data.get("current_category")
    
    if service_id in selected_services:
        selected_services.remove(service_id)
    else:
        selected_services.append(service_id)
        
    await state.update_data(selected_services=selected_services)
    
    services = await dal.get_all_services()
    from app.keyboards.inline import get_services_keyboard
    keyboard = get_services_keyboard(services, set(selected_services), current_category)
    
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()

@client_router.callback_query(F.data == "finish_service_selection")
async def finalize_service_selection(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state != ClientBooking.waiting_for_service_selection.state:
        await state.set_state(ClientBooking.waiting_for_service_selection)
    data = await state.get_data()
    selected_services = data.get("selected_services", [])
    
    if not selected_services:
        await callback.answer("Оберіть хоча б одну послугу!", show_alert=True)
        return
        
    await state.set_state(ClientBooking.waiting_for_search_wishes)
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    await callback.message.answer(
        "📝 <b>Є особливі побажання?</b>\n"
        "Напр.: довжина, техніка, колір, алергії — напиши або пропусти.\n\n"
        "<i>Я виділю майстрів, у яких є ці слова в описі профілю!</i>",
        parse_mode="HTML",
        reply_markup=get_skip_comment_keyboard(),
    )
    await callback.answer()

@client_router.message(ClientBooking.waiting_for_search_wishes, ~F.text.startswith("/"))
async def process_search_wishes(message: Message, state: FSMContext):
    await state.update_data(search_wishes=message.text)
    await process_search_after_wishes(message, state)

@client_router.callback_query(F.data == "skip_booking_comment", ClientBooking.waiting_for_search_wishes)
async def skip_search_wishes(callback: CallbackQuery, state: FSMContext):
    await state.update_data(search_wishes=None)
    await process_search_after_wishes(callback, state)
    await callback.answer()

async def process_search_after_wishes(event, state: FSMContext):
    data = await state.get_data()
    selected_services = data.get("selected_services", [])
    
    if len(selected_services) > 1:
        from app.keyboards.inline import get_match_type_keyboard
        await state.set_state(ClientBooking.waiting_for_match_type)
        msg_func = event.answer if hasattr(event, "answer") and not isinstance(event, CallbackQuery) else event.message.answer
        await msg_func(
            "Як шукати майстрів?", 
            reply_markup=get_match_type_keyboard()
        )
    else:
        await show_masters_list(event, state, match_all=True)

@client_router.callback_query(F.data == "back_to_services")
async def go_back_to_services(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientBooking.waiting_for_service_selection)
    services = await dal.get_all_services()
    data = await state.get_data()
    selected_services = data.get("selected_services", [])
    
    from app.keyboards.inline import get_categories_keyboard
    keyboard = get_categories_keyboard(services, set(selected_services))
    
    await callback.message.edit_text("Каталог послуг. Оберіть категорію:", reply_markup=keyboard)
    await callback.answer()

@client_router.callback_query(F.data.in_(["match_all", "match_any"]), ClientBooking.waiting_for_match_type)
async def process_match_type(callback: CallbackQuery, state: FSMContext):
    match_all = callback.data == "match_all"
    await show_masters_list(callback, state, match_all)

async def show_masters_list(event, state: FSMContext, match_all: bool):
    data = await state.get_data()
    selected_services = [int(sid) for sid in data.get("selected_services", [])]
    wishes = data.get("search_wishes")

    message = event.message if isinstance(event, CallbackQuery) else event
    bot = event.bot
    user_id = event.from_user.id

    previous_result_message_ids = data.get("search_master_message_ids", [])
    if previous_result_message_ids:
        for message_id in previous_result_message_ids:
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
            except Exception:
                pass
    
    masters_data = await dal.get_masters_by_services(selected_services, match_all=match_all)
    
    if not masters_data:
        await state.update_data(search_master_message_ids=[])
        from app.keyboards.inline import get_not_found_keyboard
        await message.answer(
            f"На жаль, за вашими критеріями майстрів не знайдено 😔\nСпробуйте змінити фільтри.",
            reply_markup=get_not_found_keyboard()
        )
        return
        
    print(f"[DEBUG] Preparing to show {len(masters_data)} master(s) to user {user_id}")
    result_message_ids = []
    
    for md in masters_data:
        master = md["master"]
        user = md["user"]
        matched_services = md["matched_services"]  # послуги, що відповідають пошуку
        all_services = md["all_services"]           # всі послуги майстра
        
        import re
        m_name = html.escape(user.name)
        m_desc = html.escape(master.description or "")
        
        # Highlighting logic for wishes
        if wishes and m_desc:
            words = re.findall(r'\b\w{4,}\b', wishes.lower())
            roots = [w[:4] for w in words]
            for root in roots:
                # bolding words matching the root, ignoring case
                m_desc = re.sub(
                    r'(?i)\b(' + re.escape(root) + r'\w*)\b', 
                    r'<b>\1</b>', 
                    m_desc
                )
        
        # --- Заголовок ---
        text = f"✨ <b>Майстер: {m_name}</b>\n"
        
        # --- Контакти (клікабельні) ---
        socials = []
        if master.telegram:
            tg = master.telegram.replace("@", "")
            url = f"https://t.me/{tg}"
            socials.append(f"📱 <b>Telegram:</b> <a href='{url}'>{master.telegram}</a>")
        if master.phone:
            socials.append(f"📞 <b>Телефон:</b> <a href='tel:{master.phone}'>{master.phone}</a>")
        if master.instagram:
            insta = master.instagram.replace("@", "")
            url = f"https://instagram.com/{insta}"
            socials.append(f"📸 <b>Instagram:</b> <a href='{url}'>{master.instagram}</a>")
        
        # Решта контактів без виділення (для економії місця)
        other_soc = []
        if master.whatsapp: other_soc.append("WhatsApp")
        if master.viber: other_soc.append("Viber")
        if master.facebook: other_soc.append("Facebook")
        
        if socials:
            text += "\n🔗 <b>Контакти для зв'язку:</b>\n" + "\n".join(socials) + "\n"
        if other_soc:
            text += f"<i>(Також доступний у: {', '.join(other_soc)})</i>\n"
        
        # --- Опис ---
        if m_desc:
            text += f"\n📝 <b>Про майстра:</b>\n{m_desc}\n"
        
        # --- Обрані клієнтом послуги (виділені) ---
        selected_set = set(selected_services)
        min_price = min((s["price"] for s in matched_services), default=0)
        
        text += f"\n🎯 <b>Обрані послуги:</b>\n"
        for s in matched_services:
            text += f"  ✅ <b>{html.escape(s['service_name'])}</b> — {s['price']} грн\n"
        
        # --- Інші послуги майстра ---
        other_services = [s for s in all_services if s["service_id"] not in selected_set]
        if other_services:
            text += f"\n💅 <b>Інші послуги:</b>\n"
            for s in other_services[:5]: # показуємо перші 5
                text += f"  • {html.escape(s['service_name'])} — {s['price']} грн\n"
        
        text += f"\n💰 <b>Разом:</b> від {min_price} грн"
        
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        b = InlineKeyboardBuilder()
        
        # Кнопка зв'язку в Телеграм
        if master.telegram:
            tg = master.telegram.replace("@", "")
            b.row(InlineKeyboardButton(text="💬 Написати у Telegram", url=f"https://t.me/{tg}"))
            
        b.row(InlineKeyboardButton(text=f"📅 Записатись до {m_name}", callback_data=f"book_{master.user_id}"))
        
        try:
            sent_message = await message.answer(text, reply_markup=b.as_markup(), parse_mode="HTML")
            result_message_ids.append(sent_message.message_id)
        except Exception as e:
            print(f"[ERROR] Failed to send master message: {e}")
            await message.answer(f"Помилка при виводі майстра {m_name}. Спробуйте іншого.")

    await state.update_data(search_master_message_ids=result_message_ids)
    
    if isinstance(event, CallbackQuery):
        try:
            await event.message.delete()
        except:
            pass
        await event.answer()

@client_router.callback_query(F.data.startswith("book_"))
async def start_booking(callback: CallbackQuery, state: FSMContext):
    # Case 1: Initial booking start (book_{master_id})
    if callback.data.startswith("book_") and "_" in callback.data[5:]:
         # Skip if it's some other book_ callback
         return

    master_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    result_message_ids = data.get("search_master_message_ids", [])

    if callback.message and result_message_ids:
        for message_id in result_message_ids:
            if message_id == callback.message.message_id:
                continue
            try:
                await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=message_id)
            except Exception:
                pass

    await state.update_data(master_id=master_id)
    await state.update_data(search_master_message_ids=[])
    await state.set_state(ClientBooking.waiting_for_date_time)
    
    await callback.message.edit_text(
        "📅 <b>Введіть дату та час запису:</b>\n\n"
        "Наприклад: <code>14.04 12:00</code>\n"
        "<i>(Я зчитаю лише цифри, тому формат може бути будь-яким)</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@client_router.message(ClientBooking.waiting_for_date_time, ~F.text.startswith("/"))
async def process_booking_time_text(message: Message, state: FSMContext):
    from app.utils.time_parser import parse_datetime_flexible
    from datetime import datetime
    try:
        dt = parse_datetime_flexible(message.text)
        if dt < datetime.now():
             await message.answer("❌ Цей час уже минув. Будь ласка, оберіть час у майбутньому.")
             return
    except ValueError:
        await message.answer("❌ Невірний формат! Будь ласка, введіть дату та час, наприклад: 14.04 12:00")
        return

    data = await state.get_data()
    master_id = data.get("master_id")
    selected_services = data.get("selected_services", [])
    wishes = data.get("search_wishes")

    await finalize_booking_creation(message, state, master_id, selected_services, dt, wishes)

async def finalize_booking_creation(event, state, master_id, selected_services, dt, comment=None):
    # event can be CallbackQuery or Message
    user_id = event.from_user.id
    first_service_id = selected_services[0] if selected_services else 1
    
    services = []
    for sid in selected_services:
        s = await dal.get_service_by_id(sid)
        if s: services.append(html.escape(s.name))
        
    service_names_str = ", ".join(services) if services else "Послуга"

    base_line = dt.strftime('%d.%m %H:%M')
    comment_clean = (comment or "").strip()
    
    full_comment_lines = []
    if len(selected_services) > 1:
        full_comment_lines.append(f"Обрані послуги: {service_names_str}")
    if comment_clean:
        full_comment_lines.append(f"Особливі побажання: {comment_clean}")
        
    extra_comment = "\n".join(full_comment_lines)
    booking_comment = base_line if not extra_comment else f"{base_line}\n{extra_comment}"
    
    # Створюємо запис
    booking = await dal.create_booking(
        client_id=user_id,
        master_id=master_id,
        service_id=first_service_id,
        start_time=dt,
        comment=booking_comment
    )
    
    # Повідомляємо майстра
    client_link = f"<a href='tg://user?id={user_id}'>{event.from_user.full_name}</a>"
    client_phone = "не вказано"
    c_u = await dal.get_user(user_id)
    if c_u and c_u.phone:
        client_phone = c_u.phone
    
    from app.keyboards.inline import get_booking_moderation_keyboard
    details_text = html.escape(booking.comment or base_line)
    
    await event.bot.send_message(
        chat_id=master_id,
        text=f"🆕 <b>Новий запис!</b>\n\n"
             f"👤 Клієнт: {client_link}\n"
             f"📞 Тел: <code>{client_phone}</code>\n"
             f"💅 Послуги: <b>{service_names_str}</b>\n"
             f"🧾 <b>Деталі запису:</b>\n<code>{details_text}</code>\n\n"
             f"Будь ласка, підтвердіть або запропонуйте інший час.",
        reply_markup=get_booking_moderation_keyboard(booking.id),
        parse_mode="HTML"
    )
    
    await state.set_state(ClientBooking.waiting_for_master_response)
    
    msg_text = (
        f"✅ <b>Запит відправлено!</b>\n\n"
        f"Послуги: <b>{service_names_str}</b>\n"
        f"Ви записані на <b>{dt.strftime('%d.%m %H:%M')}</b>.\n"
        f"Очікуйте на підтвердження від майстра. ⏳"
    )
    
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(msg_text, parse_mode="HTML")
    else:
        await event.answer(msg_text, reply_markup=get_start_keyboard(), parse_mode="HTML")


# (Дублікат видалено — хендлер тепер зареєстровано вище, поруч з cmd_ping)

@client_router.callback_query(F.data.startswith("agree_proposed_time_"))
async def process_agree_time(callback: CallbackQuery, state: FSMContext):
    booking_id = int(callback.data.split("_")[-1])
    
    booking = await dal.get_booking_by_id(booking_id)
    if not booking:
        await callback.answer("Запис не знайдено.", show_alert=True)
        return

    # Оновлюємо статус на CONFIRMED (час вже було оновлено майстром)
    await dal.update_booking_status(booking_id, BookingStatusEnum.CONFIRMED)
    
    await state.clear()
    await callback.message.edit_text(
        f"✅ Чудово! Ви підтвердили новий час: <b>{booking.start_time.strftime('%d.%m %H:%M')}</b>.\n"
        "Я нагадаю вам про візит за годину.",
        parse_mode="HTML"
    )
    
    # Сповіщаємо майстра
    try:
        await callback.bot.send_message(
            chat_id=booking.master_id,
            text=f"✅ Клієнт підтвердив новий час: {booking.start_time.strftime('%d.%m %H:%M')}."
        )
    except:
        pass
    await callback.answer()

@client_router.callback_query(F.data.startswith("cancel_booking_"))
async def process_cancel_booking_negotiation(callback: CallbackQuery, state: FSMContext):
    booking_id = int(callback.data.split("_")[-1])
    await dal.cancel_booking(booking_id)
    await state.clear()
    await callback.message.edit_text("❌ Бронювання скасовано.")
    
    booking = await dal.get_booking_by_id(booking_id)
    if booking:
        try:
            await callback.bot.send_message(
                chat_id=booking.master_id,
                text=f"❌ Клієнт відхилив вашу пропозицію нового часу."
            )
        except:
            pass
    await callback.answer()
    
@client_router.callback_query(F.data.startswith("client_propose_time_"))
async def client_propose_time_start(callback: CallbackQuery, state: FSMContext):
    booking_id = int(callback.data.split("_")[-1])
    await state.update_data(booking_id=booking_id)
    await state.set_state(ClientBooking.waiting_for_negotiation)
    
    from app.keyboards.main_kb import get_back_keyboard
    await callback.message.answer(
        "🕒 <b>Введіть зручний для вас час:</b>\n\n"
        "Наприклад: <code>15.04 14:30</code>",
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@client_router.message(ClientBooking.waiting_for_negotiation, ~F.text.startswith("/"))
async def process_client_counter_propose(message: Message, state: FSMContext):
    time_str = message.text.strip()
    from app.utils.time_parser import parse_datetime_flexible
    try:
        dt = parse_datetime_flexible(time_str)
        from datetime import datetime
        if dt < datetime.now():
             await message.answer("❌ Цей час вже минув. Будь ласка, оберіть час у майбутньому.")
             return
    except ValueError:
        await message.answer("❌ Невірний формат! Будь ласка, введіть дату та час, наприклад: 14.04 12:00")
        return

    data = await state.get_data()
    booking_id = data.get("booking_id")
    await state.clear()
    
    booking = await dal.get_booking_by_id(booking_id)
    if not booking:
        await message.answer("Помилка: запис не знайдено.")
        return

    # Оновлюємо статус на PENDING (повертаємо до стану очікування від майстра)
    # Але час вже новий
    await dal.propose_booking_with_time(booking_id, time_str)
    
    from app.keyboards.main_kb import get_start_keyboard
    await message.answer(
        f"✅ Вашу пропозицію на <b>{dt.strftime('%d.%m %H:%M')}</b> відправлено майстру.\n"
        f"Очікуйте на відповідь. ⏳", 
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    )
    
    # Сповіщаємо майстра
    try:
        from app.keyboards.inline import get_booking_moderation_keyboard
        client_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>"
        client_phone = booking.client.phone or "не вказано" # Тут b.client - це User об'єкт (relationship)
        
        await message.bot.send_message(
            chat_id=booking.master_id,
            text=f"🔄 <b>Клієнт запропонував інший час!</b>\n\n"
                 f"👤 Клієнт: {client_link}\n"
                 f"📞 Тел: <code>{client_phone}</code>\n"
                 f"🗓 Час: <b>{dt.strftime('%d.%m %H:%M')}</b>\n\n"
                 f"Чи підійде вам цей час?",
            reply_markup=get_booking_moderation_keyboard(booking_id),
            parse_mode="HTML"
        )
    except:
        pass

# --- Новий функціонал: Мої записи ---

@client_router.message(F.text == "📅 Мої записи")
async def show_my_bookings(message: Message):
    bookings = await dal.get_client_bookings(message.from_user.id)
    
    if not bookings:
        await message.answer("У вас поки що немає активних записів. 🌸")
        return
        
    from app.keyboards.inline import get_my_bookings_keyboard
    await message.answer(
        "📅 <b>Ваші актуальні записи:</b>\n\n"
        "⏳ — Очікує підтвердження\n"
        "✅ — Підтверджено майстром\n"
        "🔄 — Майстер запропонував інший час\n\n"
        "<i>(Ви можете скасувати запис не пізніше ніж за 2 години до початку)</i>",
        reply_markup=get_my_bookings_keyboard(bookings),
        parse_mode="HTML"
    )

@client_router.callback_query(F.data.startswith("cancel_visit_"))
async def process_cancel_visit(callback: CallbackQuery, state: FSMContext):
    booking_id = int(callback.data.split("_")[-1])
    booking = await dal.get_booking_by_id(booking_id)
    
    if not booking:
        await callback.answer("Запис не знайдено.", show_alert=True)
        return
        
    # Перевірка ліміту 2 години
    from datetime import datetime, timedelta
    now = datetime.now()
    if now > (booking.start_time - timedelta(hours=2)):
        await callback.answer(
            "На жаль, скасувати запис можна не пізніше ніж за 2 години до візиту. "
            "Будь ласка, зв'яжіться з майстром напряму.", 
            show_alert=True
        )
        return
        
    # Скасування
    await dal.cancel_booking(booking_id)
    
    # Сповіщення майстра
    try:
        master_id = booking.master_id
        time_str = booking.start_time.strftime("%d.%m %H:%M")
        
        await callback.bot.send_message(
            chat_id=master_id,
            text=f"❗️ <b>Запис скасовано клієнтом</b>\n"
                 f"👤 Клієнт: {callback.from_user.first_name}\n"
                 f"🗓 Час: {time_str}\n\n"
                 "Це вікно тепер вільне для нових записів.",
            parse_mode="HTML"
        )
    except:
        pass
        
    await callback.message.edit_text(f"✅ Запис на {booking.start_time.strftime('%d.%m %H:%M')} успішно скасовано.")
    await callback.answer("Запис скасовано.")
    await state.clear()


# --- ВІДГУКИ ---

@client_router.callback_query(F.data.startswith("review_visit_"))
async def start_review(callback: CallbackQuery, state: FSMContext):
    await state.clear() # Скидаємо будь-які старі стани
    booking_id = int(callback.data.split("_")[-1])
    await state.update_data(booking_id=booking_id)
    await state.set_state(ReviewStates.client_rating)
    
    # Клавіатура з оцінками
    kb = InlineKeyboardBuilder()
    for i in range(1, 6):
        kb.add(InlineKeyboardButton(text="⭐" * i, callback_data=f"rate_{i}"))
    kb.adjust(1)
    
    await callback.message.edit_text(
        "Будь ласка, оцініть роботу майстра:",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@client_router.callback_query(ReviewStates.client_rating, F.data.startswith("rate_"))
async def process_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[-1])
    await state.update_data(rating=rating)
    await state.set_state(ReviewStates.client_comment)
    
    await callback.message.edit_text(
        f"Ви обрали {rating} ⭐\nТепер напишіть короткий коментар про ваш візит (або натисніть кнопку нижче, щоб пропустити):",
        reply_markup=InlineKeyboardBuilder().row(
            InlineKeyboardButton(text="Пропустити ⏭️", callback_data="skip_comment")
        ).as_markup()
    )
    await callback.answer()

@client_router.message(ReviewStates.client_comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text
    data = await state.get_data()
    await finish_booking_review(message, state, data['booking_id'], data['rating'], comment)

@client_router.callback_query(ReviewStates.client_comment, F.data == "skip_comment")
async def skip_comment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await finish_booking_review(callback.message, state, data['booking_id'], data['rating'], None)
    await callback.answer()

async def finish_booking_review(message, state, booking_id, rating, comment):
    from app.database.models import RoleEnum
    from app.keyboards.main_kb import get_main_keyboard
    await dal.add_booking_review(booking_id, RoleEnum.CLIENT, rating, comment)
    await state.clear()
    
    text = "Дякуємо за ваш відгук! ❤️ Він допоможе іншим клієнтам обрати найкращого майстра."
    if isinstance(message, Message):
        await message.answer(text, reply_markup=get_main_keyboard())
    else:
        await message.edit_text(text)
@client_router.callback_query(F.data == "back_to_main")
async def process_back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Повернення до головного меню.", reply_markup=get_start_keyboard())
    await callback.answer()
