import html
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from app.keyboards.main_kb import get_cancel_keyboard, get_master_menu_keyboard, get_start_keyboard
from app.keyboards.inline import get_master_services_keyboard, get_social_links_menu
from app.states.registration import MasterRegistration
from app.states.master_profile import MasterProfileStates
from app.states.review_states import ReviewStates
from app.database import dal
from app.database.models import RoleEnum, BookingStatusEnum

master_router = Router()

@master_router.message(F.text == "💼 Я майстер")
async def start_master_registration(message: Message, state: FSMContext):
    master = await dal.get_master(message.from_user.id)
    if master:
        await message.answer("Ви вже зареєстровані як майстер! Вітаю в панелі управління. 💅", reply_markup=get_master_menu_keyboard())
        return

    from app.keyboards.main_kb import get_back_keyboard
    await state.set_state(MasterRegistration.waiting_for_name)
    await message.answer("Чудово! Давайте створимо ваш профіль.\n\nЯк вас звати? (Це ім'я будуть бачити клієнти)", reply_markup=get_back_keyboard())

@master_router.message(MasterRegistration.waiting_for_name, ~F.text.contains("Повернутись"), ~F.text.contains("Скасувати"))
async def process_master_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(MasterRegistration.waiting_for_description)
    await message.answer("Опишіть себе та вашу справу. Що саме ви пропонуєте клієнтам?")

@master_router.message(MasterRegistration.waiting_for_description, ~F.text.contains("Повернутись"), ~F.text.contains("Скасувати"))
async def process_master_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    # Переходимо до вибору контактів
    await state.set_state(MasterProfileStates.choosing_social_net)
    await message.answer(
        "Тепер додамо ваші контакти та соцмережі.\n"
        "Оберіть мережу, яку хочете додати (бажано хоча б одну):",
        reply_markup=get_social_links_menu()
    )

@master_router.callback_query(F.data.startswith("edit_social_"), MasterProfileStates.choosing_social_net)
async def process_choosing_social(callback: CallbackQuery, state: FSMContext):
    social_type = callback.data.replace("edit_social_", "")
    await state.update_data(current_social=social_type)
    await state.set_state(MasterProfileStates.entering_social_link)
    
    if social_type == "phone":
        prompt = "Введіть номер телефону (наприклад: 0971996058).\nПрефікс +380 вже враховано:"
    else:
        # Простий мапінг для красивого відображення
        names = {"instagram": "Instagram", "facebook": "Facebook", "tiktok": "TikTok", 
                 "telegram": "Telegram", "whatsapp": "WhatsApp", "viber": "Viber", "website": "Сайт"}
        name = names.get(social_type, social_type.capitalize())
        prompt = f"Введіть нікнейм або посилання для {name}:"
        
    await callback.message.edit_text(prompt)
    await callback.answer()

@master_router.message(MasterProfileStates.entering_social_link, ~F.text.contains("Повернутись"), ~F.text.contains("Скасувати"))
async def process_entering_social(message: Message, state: FSMContext):
    data = await state.get_data()
    social_type = data['current_social']
    social_links = data.get('social_links', {})
    
    val = message.text.strip()
    if social_type == "phone":
        import re
        nums = re.sub(r'\D', '', val)
        if len(nums) == 9: # 971234567
            val = f"+380{nums}"
        elif len(nums) == 10: # 0971234567
            val = f"+380{nums[1:]}"
        elif len(nums) == 12 and nums.startswith("380"): # 380971234567
            val = f"+{nums}"
        elif not val.startswith("+"):
            # Якщо нічого не підійшло, але немає +, намагаємось додати хоча б +380 якщо цифр мало
            if len(nums) < 10:
                val = f"+380{nums}"
            else:
                val = f"+{nums}"
            
    social_links[social_type] = val
    
    await state.update_data(social_links=social_links)
    await state.set_state(MasterProfileStates.choosing_social_net)
    
    names = {"instagram": "Instagram", "facebook": "Facebook", "tiktok": "TikTok", 
             "telegram": "Telegram", "whatsapp": "WhatsApp", "viber": "Viber", "phone": "Телефон", "website": "Сайт"}
    
    links_text = "\n".join([f"✅ {names.get(k, k.capitalize())}: {v}" for k, v in social_links.items()])
    await message.answer(
        f"Збережено!\n\nВаші контакти:\n{links_text}\n\nБажаєте додати ще щось?",
        reply_markup=get_social_links_menu()
    )

@master_router.callback_query(F.data == "finish_social_links", MasterProfileStates.choosing_social_net)
async def finish_social_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # 1. Спробуємо знайти майстра або створити його
    master = await dal.get_master(callback.from_user.id)
    social_links = data.get('social_links', {})
    
    # Якщо ми в процесі реєстрації, у нас є опис у стейті
    description = data.get('description', master.description if master else "Новий майстер")
    
    # Переконуємось, що User взагалі існує (якщо базу скинули, а користувач не натискав /start)
    user = await dal.get_user(callback.from_user.id)
    if not user:
        await dal.create_user(
            telegram_id=callback.from_user.id,
            name=callback.from_user.first_name,
            role=RoleEnum.MASTER
        )
    else:
        # Оновлюємо ім'я (якщо він його вводив) та роль
        input_name = data.get('name')
        if input_name and input_name != user.name:
            # Оновимо ім'я
            async with dal.async_session() as session:
                from sqlalchemy import select
                u = await session.execute(select(dal.User).where(dal.User.telegram_id == callback.from_user.id))
                u = u.scalars().first()
                if u:
                    u.name = input_name
                    await session.commit()
    
    # Оновлюємо або створюємо
    await dal.update_user_role(callback.from_user.id, RoleEnum.MASTER)
    
    try:
        await dal.create_master(
            user_id=callback.from_user.id,
            description=description
        )
    except Exception as e:
        print(f"[ERROR] Failed to create master: {e}")
        await callback.answer("Виникла помилка. Натисніть /start і спробуйте знову.", show_alert=True)
        return
    # Оновлюємо соціальні посилання
    if social_links:
        await dal.update_master_profile(callback.from_user.id, **social_links)
    
    # 2. Визначаємо куди йти далі
    # Якщо це вперше (немає послуг) - йдемо на вибір послуг
    has_services = await dal.master_has_services(callback.from_user.id)
    if not has_services:
        await state.set_state(MasterProfileStates.choosing_service_category) 
        services = await dal.get_all_services()
        await state.update_data(selected_services=[])
        
        from app.keyboards.inline import get_categories_keyboard
        await callback.message.edit_text(
            "🎉 Профіль підготовлено! Тепер оберіть категорію послуг, які ви надаєте:",
            reply_markup=get_categories_keyboard(services, set(), is_master=True)
        )
    else:
        await state.clear()
        await callback.message.edit_text("✅ Зміни успішно збережені!")
        # Визиваємо показ профілю
        await show_profile(callback.message)
    
    await callback.answer()

@master_router.callback_query(F.data.startswith("select_m_cat_"), MasterProfileStates.choosing_service_category)
async def process_master_category_selection(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace("select_m_cat_", "")
    await state.update_data(current_category=category)
    
    services = await dal.get_all_services()
    data = await state.get_data()
    selected = set(data.get("selected_services", []))
    
    from app.keyboards.inline import get_master_services_keyboard
    keyboard = get_master_services_keyboard(services, selected, category)
    
    await callback.message.edit_text(f"📂 <b>Категорія: {category}</b>\nОберіть послуги, які ви надаєте:", reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@master_router.callback_query(F.data == "back_to_m_categories", MasterProfileStates.choosing_service_category)
async def back_to_m_categories_callback(callback: CallbackQuery, state: FSMContext):
    services = await dal.get_all_services()
    data = await state.get_data()
    selected = set(data.get("selected_services", []))
    
    from app.keyboards.inline import get_categories_keyboard
    keyboard = get_categories_keyboard(services, selected, is_master=True)
    
    await callback.message.edit_text("Оберіть категорію послуг:", reply_markup=keyboard)
    await callback.answer()

@master_router.callback_query(F.data.startswith("mserv_"), MasterProfileStates.choosing_service_category)
async def process_master_service_toggle(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    services = await dal.get_all_services()
    data = await state.get_data()
    selected = set(data.get("selected_services", []))
    current_category = data.get("current_category")
    
    if service_id in selected:
        selected.remove(service_id)
    else:
        selected.add(service_id)
        # Якщо обрано "Інше" — показуємо пояснення
        service = next((s for s in services if s.id == service_id), None)
        if service and service.name == "Інше":
            await callback.answer(
                "💡 Ви обрали 'Інше'.\n\n"
                "Це послуга для індивідуальних запитів. Коли клієнт обере її, він зможе описати свою потребу текстом, і ви отримаєте цей опис у запиті.",
                show_alert=True
            )
        
    await state.update_data(selected_services=list(selected))
    from app.keyboards.inline import get_master_services_keyboard
    await callback.message.edit_reply_markup(reply_markup=get_master_services_keyboard(services, selected, current_category))
    await callback.answer()

@master_router.callback_query(F.data == "propose_new_service")
async def start_proposing_service(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MasterProfileStates.proposing_service)
    await callback.message.answer("Введіть назву послуги, яку ви хочете додати (наприклад: 'Ламінування вій'):")
    await callback.answer()

@master_router.message(MasterProfileStates.proposing_service, ~F.text.contains("Повернутись"), ~F.text.contains("Скасувати"))
async def process_proposing_service(message: Message, state: FSMContext):
    service_name = message.text
    # Створюємо пропозицію
    await dal.create_service_proposal(message.from_user.id, service_name)
    
    await message.answer(
        f"Дякуємо! Послуга '{service_name}' відправлена на модерацію. "
        "Вона з'явиться в списку після підтвердження адміністратором."
    )
    # Повертаємо стан до вибору категорій
    await state.set_state(MasterProfileStates.choosing_service_category)
    services = await dal.get_all_services()
    data = await state.get_data()
    selected = set(data.get("selected_services", []))
    from app.keyboards.inline import get_categories_keyboard
    await message.answer("Ви можете обрати ще інші існуючі послуги:", reply_markup=get_categories_keyboard(services, selected, is_master=True))

@master_router.callback_query(F.data == "save_master_services")
async def finish_master_services(callback: CallbackQuery, state: FSMContext):
    # Перевіряємо стан - якщо не той, значить натиснули стару кнопку після перезапуску бота
    current_state = await state.get_state()
    if current_state != MasterProfileStates.choosing_service_category.state:
        await callback.answer(
            "⚠️ Сесія застаріла. Натисніть '➕ Додати послугу' щоб почати знову.",
            show_alert=True
        )
        return

    data = await state.get_data()
    selected_ids = data.get("selected_services", [])
    
    if not selected_ids:
        await callback.answer("Оберіть хоча б одну послугу!", show_alert=True)
        return
    
    # Отримуємо існуючі ціни з БД
    existing_prices = await dal.get_master_services_prices(callback.from_user.id)
    
    # Визначаємо послуги, для яких ще немає ціни
    services_to_price = [sid for sid in selected_ids if str(sid) not in existing_prices]
    
    # Залишаємо вже зібрані ціни для послуг, які були обрані і вже мали ціну
    prices_collected = {str(sid): existing_prices[str(sid)] for sid in selected_ids if str(sid) in existing_prices}

    if not services_to_price:
        # Всі обрані послуги вже мають ціну, зберігаємо і виходимо
        await dal.set_master_services(callback.from_user.id, prices_collected)
        count = len(prices_collected)
        await state.clear()
        
        # Видаляємо старе сповіщення з каталогом
        try:
            await callback.message.delete()
        except Exception:
            pass
            
        await callback.message.answer(
            f"🎉 <b>Готово!</b> {count} {'послуга збережена' if count == 1 else 'послуги збережено'}!\n\n"
            f"Ваш профіль активний і клієнти вже можуть вас знайти. 💅",
            reply_markup=get_master_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    # Запускаємо цикл збору цін для НОВИХ послуг
    await state.update_data(services_to_price=list(services_to_price), price_index=0, prices_collected=prices_collected)
    await state.set_state(MasterProfileStates.entering_service_price)
    
    first_service = await dal.get_service_by_id(services_to_price[0])
    service_name = first_service.name if first_service else f"Послуга #{services_to_price[0]}"
    total = len(services_to_price)
    
    # Видаляємо старе сповіщення з каталогом
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    # Надсилаємо нове чітке повідомлення з запитом ціни
    await callback.message.answer(
        f"💰 Тепер вкажіть ціни для доданих послуг (одна за одною).\n\n"
        f"💅 <b>{html.escape(service_name)}</b> (1/{total})\n\n"
        f"Напишіть мінімальну ціну в грн (\u043dаприклад: <b>500</b>):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@master_router.message(MasterProfileStates.entering_service_price, ~F.text.contains("Повернутись"), ~F.text.contains("Скасувати"))
async def process_service_price(message: Message, state: FSMContext):
    # Перевірка введеної ціни
    try:
        price = int(message.text.strip())
        if price < 0:
            raise ValueError("negative")
    except (ValueError, AttributeError):
        await message.answer("⚠️ Будь ласка, введіть ціле позитивне число (наприклад: <b>500</b>)", parse_mode="HTML")
        return
    
    data = await state.get_data()
    services_to_price = data.get("services_to_price", [])
    price_index = data.get("price_index", 0)
    prices_collected = data.get("prices_collected", {})
    
    # Зберігаємо ціну для поточної послуги
    current_service_id = services_to_price[price_index]
    prices_collected[str(current_service_id)] = price
    
    next_index = price_index + 1
    await state.update_data(prices_collected=prices_collected, price_index=next_index)
    
    if next_index < len(services_to_price):
        # Запитуємо ціну для наступної послуги
        next_service_id = services_to_price[next_index]
        next_service = await dal.get_service_by_id(next_service_id)
        service_name = next_service.name if next_service else f"Послуга #{next_service_id}"
        
        progress = f"({next_index + 1}/{len(services_to_price)})"
        await message.answer(
            f"✅ Збережено!\n\n"
            f"💅 <b>{html.escape(service_name)}</b> {progress}\n\n"
            f"Напишіть мінімальну ціну в грн (наприклад: <b>500</b>):",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
    else:
        # Всі ціни зібрано — зберігаємо в БД
        await dal.set_master_services(message.from_user.id, prices_collected)
        
        count = len(prices_collected)
        await state.clear()
        await message.answer(
            f"🎉 <b>Готово!</b> {count} {'послуга збережена' if count == 1 else 'послуги збережено'}!\n\n"
            f"Ваш профіль активний і клієнти вже можуть вас знайти. 💅",
            reply_markup=get_master_menu_keyboard(),
            parse_mode="HTML"
        )


@master_router.message(F.text == "👤 Мій профіль")
async def show_profile(message: Message):
    master = await dal.get_master(message.from_user.id)
    if not master:
        await message.answer("Профіль не знайдено.")
        return
    
    # Визначаємо список заповнених контактів з іконками та посиланнями
    socials = []
    if master.phone: 
        socials.append(f"📞 <b>Телефон:</b> <a href='tel:{master.phone}'>{master.phone}</a>")
    if master.instagram: 
        insta = master.instagram.replace("@", "")
        url = f"https://instagram.com/{insta}"
        socials.append(f"📸 <b>Instagram:</b> <a href='{url}'>{master.instagram}</a>")
    if master.telegram: 
        tg = master.telegram.replace("@", "")
        url = f"https://t.me/{tg}"
        socials.append(f"📱 <b>Telegram:</b> <a href='{url}'>{master.telegram}</a>")
    if master.viber: socials.append(f"🟣 <b>Viber:</b> {master.viber}")
    if master.whatsapp: socials.append(f"💬 <b>WhatsApp:</b> {master.whatsapp}")
    if master.facebook: 
        fb = master.facebook.replace("@", "")
        url = f"https://facebook.com/{fb}"
        socials.append(f"📘 <b>Facebook:</b> <a href='{url}'>{master.facebook}</a>")
    if master.tiktok: socials.append(f"🎞 <b>TikTok:</b> {master.tiktok}")
    if master.website: socials.append(f"🌐 <b>Сайт:</b> <a href='{master.website}'>{master.website}</a>")
    
    socials_text = "\n".join(socials) if socials else "<i>Контакти ще не додані</i>"
    
    # Отримуємо послуги майстра
    services = await dal.get_master_services_full(message.from_user.id)
    services_text = ""
    if services:
        services_text = "\n".join([f"  • {html.escape(s['name'])} — {s['price']} грн" for s in services])
    else:
        services_text = "<i>Послуги ще не додані</i>"

    text = (
        f"✨ <b>ВАШ ПУБЛІЧНИЙ ПРОФІЛЬ</b> ✨\n\n"
        f"📝 <b>Про вас:</b>\n{master.description}\n\n"
        f"💅 <b>Ваші послуги:</b>\n{services_text}\n\n"
        f"🔗 <b>Ваші контакти для зв'язку:</b>\n{socials_text}\n"
    )

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📝 Змінити опис", callback_data="master_edit_desc"))
    kb.row(InlineKeyboardButton(text="📱 Додати/Змінити контакти", callback_data="master_edit_contacts"))
    kb.row(InlineKeyboardButton(text="💅 Керувати послугами", callback_data="master_edit_services"))
    
    await message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())

@master_router.callback_query(F.data == "master_edit_desc")
async def edit_desc_start(callback: CallbackQuery, state: FSMContext):
    from app.keyboards.main_kb import get_back_keyboard
    await state.set_state(MasterProfileStates.editing_description)
    await callback.message.answer("Введіть новий опис вашого профілю:", reply_markup=get_back_keyboard())
    await callback.answer()

@master_router.message(MasterProfileStates.editing_description, ~F.text.contains("Повернутись"), ~F.text.contains("Скасувати"))
async def process_new_description(message: Message, state: FSMContext):
    await dal.update_master_profile(message.from_user.id, description=message.text)
    await state.clear()
    await message.answer("✅ Опис успішно оновлено!", reply_markup=get_master_menu_keyboard())
    await show_profile(message)

@master_router.callback_query(F.data == "master_edit_contacts")
async def edit_contacts_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MasterProfileStates.choosing_social_net)
    await callback.message.edit_text("Оберіть контакт, який хочете додати або змінити:", reply_markup=get_social_links_menu())
    await callback.answer()

@master_router.callback_query(F.data == "master_edit_services")
async def master_edit_services(callback: CallbackQuery, state: FSMContext):
    # 1. Отримуємо поточні послуги майстра
    master_id = callback.from_user.id
    current_service_ids = await dal.get_master_service_ids(master_id)
    
    # 2. Ініціалізуємо стан
    await state.update_data(selected_services=list(current_service_ids))
    await state.set_state(MasterProfileStates.choosing_service_category)
    
    # 3. Показуємо категорії
    services = await dal.get_all_services()
    from app.keyboards.inline import get_categories_keyboard
    keyboard = get_categories_keyboard(services, current_service_ids, is_master=True)
    
    await callback.message.edit_text(
        "💅 <b>Керування вашими послугами</b>\n\n"
        "Оберіть категорію, щоб змінити список послуг. "
        "Послуги, які ви вже надаєте, відмічені галочкою ✅.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

# --- Обробка записів від клієнтів ---

@master_router.callback_query(F.data.startswith("master_confirm_"))
async def master_confirm_booking(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[-1])
    booking = await dal.get_booking_by_id(booking_id)
    
    if not booking:
        await callback.answer("Запис не знайдено.", show_alert=True)
        return

    await dal.update_booking_status(booking_id, BookingStatusEnum.CONFIRMED)
    await callback.message.edit_text(f"✅ Ви підтвердили запис на {booking.start_time.strftime('%d.%m %H:%M')}.")
    
    # Сповіщення клієнту
    try:
        details = await dal.get_booking_full_details(booking_id)
        if details:
            m_user = details["master_user"]
            m_prof = details["master_profile"]
            # Пріоритет телефону: з профілю майстра, інакше з User
            m_phone = m_prof.phone or m_user.phone or "не вказано"
            # Пріоритет телеграм: з профілю майстра (якщо це лінк або юзернейм), інакше через id
            if m_prof.telegram:
                 m_tg = m_prof.telegram.replace("@", "")
                 m_link = f"<a href='https://t.me/{m_tg}'>{m_prof.telegram}</a>"
            else:
                 m_link = f"<a href='tg://user?id={m_user.telegram_id}'>{m_user.name}</a>"
            
            await callback.bot.send_message(
                chat_id=booking.client_id,
                text=f"✅ <b>Майстер підтвердив ваш запис!</b>\n\n"
                     f"🗓 Час: <b>{booking.start_time.strftime('%d.%m %H:%M')}</b>\n"
                     f"👤 Майстер: {m_link}\n"
                     f"📞 Тел: <code>{m_phone}</code>\n\n"
                     f"Я нагадаю вам про візит за годину. До зустрічі! ✨",
                parse_mode="HTML"
            )
    except:
        pass
    await callback.answer()

@master_router.callback_query(F.data.startswith("master_reject_"))
async def master_reject_booking(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[-1])
    await dal.update_booking_status(booking_id, BookingStatusEnum.REJECTED)
    
    await callback.message.edit_text("❌ Ви відхилили запис.")
    
    # Сповіщення клієнту
    booking = await dal.get_booking_by_id(booking_id)
    if booking:
        try:
            await callback.bot.send_message(
                chat_id=booking.client_id,
                text="😔 На жаль, майстер відхилив ваш запис на цей час. Спробуйте обрати інший час або іншого майстра."
            )
        except:
            pass
    await callback.answer()

@master_router.callback_query(F.data.startswith("master_propose_"))
async def master_propose_start(callback: CallbackQuery, state: FSMContext):
    booking_id = int(callback.data.split("_")[-1])
    await state.update_data(booking_id=booking_id)
    await state.set_state(MasterProfileStates.proposing_time)
    
    from app.keyboards.main_kb import get_back_keyboard
    await callback.message.answer(
        "Введіть новий час для клієнта (наприклад: <b>14.04 12:00</b>):\n"
        "<i>(Я зчитаю лише цифри, тому формат може бути будь-яким)</i>",
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@master_router.message(MasterProfileStates.proposing_time, ~F.text.contains("Повернутись"), ~F.text.contains("Скасувати"))
async def process_master_propose_time(message: Message, state: FSMContext):
    time_str = message.text.strip()
    from app.utils.time_parser import parse_datetime_flexible
    from datetime import datetime
    try:
        # Перевіряємо формат та чи не в минулому
        dt = parse_datetime_flexible(time_str)
        if dt < datetime.now():
             await message.answer("❌ Ви намагаєтесь запропонувати час, який вже минув. Оберіть час у майбутньому.")
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

    formatted_time = dt.strftime("%d.%m %H:%M")

    # Оновлюємо час у БД зі статусом PROPOSED
    await dal.propose_booking_with_time(booking_id, time_str)
    
    await message.answer(f"✅ Пропозицію на <b>{formatted_time}</b> відправлено клієнту.", reply_markup=get_master_menu_keyboard(), parse_mode="HTML")
    
    try:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text=f"✅ Погодитись на {formatted_time}", callback_data=f"agree_proposed_time_{booking_id}"))
        kb.row(InlineKeyboardButton(text="⏳ Запропонувати інший час", callback_data=f"client_propose_time_{booking_id}"))
        kb.row(InlineKeyboardButton(text="❌ Відмінити", callback_data=f"cancel_booking_{booking_id}"))

        details = await dal.get_booking_full_details(booking_id)
        m_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>"
        m_phone = "не вказано"
        
        if details:
            m_user = details["master_user"]
            m_prof = details["master_profile"]
            m_phone = m_prof.phone or m_user.phone or "не вказано"
            if m_prof.telegram:
                 m_tg = m_prof.telegram.replace("@", "")
                 m_link = f"<a href='https://t.me/{m_tg}'>{m_prof.telegram}</a>"
            else:
                 m_link = f"<a href='tg://user?id={m_user.telegram_id}'>{m_user.name}</a>"

        await message.bot.send_message(
            chat_id=booking.client_id,
            text=f"🔄 <b>Майстер запропонував інший час!</b>\n\n"
                 f"👤 Майстер: {m_link}\n"
                 f"📞 Тел: <code>{m_phone}</code>\n"
                 f"Чи підійде вам <b>{formatted_time}</b>?",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
    except:
        pass


# --- ВІДГУКИ ПРО КЛІЄНТІВ ---

@master_router.callback_query(F.data.startswith("master_review_visit_"))
async def master_start_review(callback: CallbackQuery, state: FSMContext):
    await state.clear() # Скидаємо будь-які старі стани
    booking_id = int(callback.data.split("_")[-1])
    await state.update_data(booking_id=booking_id)
    await state.set_state(ReviewStates.master_rating)
    
    # Клавіатура з оцінками
    kb = InlineKeyboardBuilder()
    for i in range(1, 6):
        kb.add(InlineKeyboardButton(text="⭐" * i, callback_data=f"mrate_{i}"))
    kb.adjust(1)
    
    await callback.message.edit_text(
        "Як пройшов візит клієнта? Будь ласка, оцініть співпрацю:",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@master_router.callback_query(ReviewStates.master_rating, F.data.startswith("mrate_"))
async def master_process_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[-1])
    await state.update_data(rating=rating)
    await state.set_state(ReviewStates.master_comment)
    
    await callback.message.edit_text(
        f"Ви обрали {rating} ⭐\nДодайте короткий коментар (наприклад, про пунктуальність):",
        reply_markup=InlineKeyboardBuilder().row(
            InlineKeyboardButton(text="Пропустити ⏭️", callback_data="master_skip_comment")
        ).as_markup()
    )
    await callback.answer()

@master_router.message(ReviewStates.master_comment)
async def master_process_comment(message: Message, state: FSMContext):
    comment = message.text
    data = await state.get_data()
    await finish_master_review(message, state, data['booking_id'], data['rating'], comment)

@master_router.callback_query(ReviewStates.master_comment, F.data == "master_skip_comment")
async def master_skip_comment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await finish_master_review(callback.message, state, data['booking_id'], data['rating'], None)
    await callback.answer()

async def finish_master_review(message, state, booking_id, rating, comment):
    from app.database.models import RoleEnum
    await dal.add_booking_review(booking_id, RoleEnum.MASTER, rating, comment)
    await state.clear()
    
    text = "✅ Відгук про клієнта успішно збережено. Дякуємо!"
    if isinstance(message, Message):
        await message.answer(text, reply_markup=get_master_menu_keyboard())
    else:
        await message.edit_text(text)
