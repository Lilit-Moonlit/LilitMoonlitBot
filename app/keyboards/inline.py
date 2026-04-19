from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.models import Service
from app.catalog import CATALOG_CATEGORY_ORDER

# Мапа емодзі та порядок категорій (від популярних до інших)
CATEGORY_EMOJIS = {
    "Волосся": "✂️",
    "Нігті": "💅",
    "Брови та вії": "👁️",
    "Обличчя та косметологія": "🧴",
    "Епіляція/депіляція": "🍯",
    "Додатково": "🔹"
}

# Визначаємо порядок відображення категорій
CATEGORY_ORDER = CATALOG_CATEGORY_ORDER

def shorten_service_name(category: str, service_name: str) -> str:
    """Видаляє зайві приставки для максимально чистого інтерфейсу"""
    if not category:
        return service_name
    
    # Ретельне скорочення: якщо назва категорії є частиною назви послуги
    # Або якщо послуга починається з очевидних слів
    name = service_name.strip()
    
    # 1. Якщо категорія "Масаж" і послуга "Масаж спини" -> "Спини"
    cat_clear = category.split()[0].lower() # беремо перше слово категорії (н-ад "Нігтьовий" -> "нігтьовий")
    if name.lower().startswith(cat_clear):
        name = name[len(cat_clear):].strip()
        
    # 2. Спеціальні скорочення для поширених груп (навіть якщо вони не в назві категорії)
    prefixes_to_strip = ["Манікюр", "Педикюр", "Масаж", "Стрижка"]
    for p in prefixes_to_strip:
        if name.lower().startswith(p.lower()) and len(name) > len(p) + 2:
            # Тільки якщо після префікса є ще слова (н-ад "Масаж спини" -> "спини", але "Масаж" лишаємо)
            name = name[len(p):].strip()
            # Додаємо префікс назад коротким символом або просто лишаємо коротку назву
            break
            
    return name.capitalize() if name else service_name

def get_categories_keyboard(services: list[Service], selected_ids: set[int], is_master: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    cat_counts = {}
    total_selected = len(selected_ids)
    
    # Витягуємо всі категорії, що реально існують у списку послуг
    existing_cats = set(s.category or "Інше" for s in services)
    
    # Будуємо список категорій відповідно до CATEGORY_ORDER
    categories_list = []
    for cat in CATEGORY_ORDER:
        if cat in existing_cats:
            categories_list.append(cat)
            existing_cats.remove(cat)
    # Додаємо залишки (якщо вони є)
    categories_list.extend(sorted(list(existing_cats)))

    for s in services:
        if s.id in selected_ids:
            cat = s.category or "Інше"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat in categories_list:
        emoji = CATEGORY_EMOJIS.get(cat, "🔹")
        count = cat_counts.get(cat, 0)
        if count > 0:
            label = f"{emoji} ({count}) {cat}"
        else:
            label = f"{emoji} {cat}"
        callback = f"select_m_cat_{cat}" if is_master else f"select_cat_{cat}"
        builder.button(text=label, callback_data=callback)
    builder.adjust(2)
    if total_selected > 0:
        finish_text = "ЗБЕРЕГТИ ОБРАНЕ ➡️" if is_master else "🔍 ПЕРЕЙТИ ДО ПОШУКУ 🔍"
        callback = "save_master_services" if is_master else "finish_service_selection"
        builder.row(InlineKeyboardButton(text=finish_text, callback_data=callback))
    builder.row(InlineKeyboardButton(text="🔙 Повернутись до меню", callback_data="back_to_main"))
    return builder.as_markup()

def get_services_keyboard(services: list[Service], selected_ids: set[int], category_filter: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    cat_services = [s for s in services if (s.category or "Інше") == category_filter]
    for s in cat_services:
        mark = "✅ " if s.id in selected_ids else ""
        display_name = shorten_service_name(category_filter, s.name)
        builder.button(text=f"{mark}{display_name}", callback_data=f"serv_{s.id}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 До категорій", callback_data="back_to_categories"))
    if selected_ids:
        builder.row(InlineKeyboardButton(text="🔍 ПЕРЕЙТИ ДО ПОШУКУ 🔍", callback_data="finish_service_selection"))
    return builder.as_markup()

def get_master_services_keyboard(services: list[Service], selected_ids: set[int], category_filter: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    cat_services = [s for s in services if (s.category or "Інше") == category_filter]
    for s in cat_services:
        mark = "✅ " if s.id in selected_ids else ""
        display_name = shorten_service_name(category_filter, s.name)
        builder.button(text=f"{mark}{display_name}", callback_data=f"mserv_{s.id}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 До категорій", callback_data="back_to_m_categories"))
    builder.row(InlineKeyboardButton(text="➕ Запропонувати нову", callback_data="propose_new_service"))
    if selected_ids:
        builder.row(InlineKeyboardButton(text="Зберегти обрані ➡️", callback_data="save_master_services"))
    return builder.as_markup()

def get_social_links_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📸 Instagram", callback_data="edit_social_instagram"))
    builder.row(InlineKeyboardButton(text="📘 Facebook", callback_data="edit_social_facebook"))
    builder.row(InlineKeyboardButton(text="🎞 TikTok", callback_data="edit_social_tiktok"))
    builder.row(InlineKeyboardButton(text="📱 Telegram", callback_data="edit_social_telegram"))
    builder.row(InlineKeyboardButton(text="💬 WhatsApp", callback_data="edit_social_whatsapp"))
    builder.row(InlineKeyboardButton(text="🟣 Viber", callback_data="edit_social_viber"))
    builder.row(InlineKeyboardButton(text="📞 Телефон", callback_data="edit_social_phone"))
    builder.row(InlineKeyboardButton(text="🌐 Сайт", callback_data="edit_social_website"))
    builder.row(InlineKeyboardButton(text="✅ Завершити", callback_data="finish_social_links"))
    return builder.as_markup()

def get_moderation_keyboard(proposal_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Підтвердити", callback_data=f"admin_approve_{proposal_id}"),
        InlineKeyboardButton(text="❌ Відхилити", callback_data=f"admin_reject_{proposal_id}")
    )
    return builder.as_markup()

def get_booking_moderation_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    """Клавіатура для майстра при отриманні нового запису."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Підтвердити", callback_data=f"master_confirm_{booking_id}"),
        InlineKeyboardButton(text="❌ Відхилити", callback_data=f"master_reject_{booking_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🖊 Запропонувати інший час", callback_data=f"master_propose_{booking_id}")
    )
    return builder.as_markup()

def get_match_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Показати з УСІМА послугами", callback_data="match_all"))
    builder.row(InlineKeyboardButton(text="Показати з ХОЧА Б ОДНІЄЮ", callback_data="match_any"))
    builder.row(InlineKeyboardButton(text="🔙 Назад до вибору", callback_data="back_to_services"))
    return builder.as_markup()

def get_my_bookings_keyboard(bookings: list) -> InlineKeyboardMarkup:
    from datetime import datetime, timedelta
    from app.database.models import BookingStatusEnum
    builder = InlineKeyboardBuilder()
    now = datetime.now()
    
    for b in bookings:
        time_str = b.start_time.strftime("%d.%m %H:%M")
        status = b.status
        
        # Визначаємо емодзі статусу
        status_emoji = "⏳"
        status_text = ""
        if status == BookingStatusEnum.CONFIRMED:
            status_emoji = "✅"
        elif status == BookingStatusEnum.PROPOSED:
            status_emoji = "🔄"
            status_text = " (Пропозиція)"
        elif status == BookingStatusEnum.PENDING:
            status_emoji = "⏳"
            status_text = " (Очікує)"
        elif status == BookingStatusEnum.COMPLETED:
            status_emoji = "🏁"
            
        # 1. Якщо візит вже у МИНУЛОМУ (або вже COMPLETED)
        if b.end_time < now or status == BookingStatusEnum.COMPLETED:
            if not getattr(b, 'is_reviewed_by_client', False):
                builder.row(InlineKeyboardButton(text=f"{status_emoji} {time_str} - ⭐ Відгук", callback_data=f"review_visit_{b.id}"))
            else:
                builder.row(InlineKeyboardButton(text=f"{status_emoji} {time_str} - Завершено", callback_data="none"))
        
        # 2. Якщо візит скоро (< 2 годин)
        elif b.start_time - timedelta(hours=2) < now:
            builder.row(InlineKeyboardButton(text=f"{status_emoji} {time_str} - 🔒 (Закріплено)", callback_data=f"locked_visit_{b.id}"))
            
        # 3. Майбутній візит (> 2 годин)
        else:
            if status == BookingStatusEnum.PROPOSED:
                # Якщо це пропозиція від майстра, даємо можливість перейти до неї
                builder.row(InlineKeyboardButton(text=f"{status_emoji} {time_str}{status_text}", callback_data=f"client_propose_time_{b.id}"))
            else:
                builder.row(InlineKeyboardButton(text=f"{status_emoji} {time_str}{status_text} - ❌ Скасувати", callback_data=f"cancel_visit_{b.id}"))
    
    return builder.as_markup()

def get_not_found_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Змінити вибір послуг", callback_data="back_to_services"))
    return builder.as_markup()

def get_date_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Генерує клавіатуру на 3 найближчі дні"""
    from datetime import datetime, timedelta
    builder = InlineKeyboardBuilder()
    
    days = ["Сьогодні", "Завтра", "Післязавтра"]
    
    for i in range(3):
        dt = datetime.now() + timedelta(days=i)
        day_str = dt.strftime("%d.%m")
        btn_text = f"{days[i]} ({day_str})"
        callback = f"{prefix}_{dt.strftime('%d%m')}" # e.g. cdate_0604
        builder.row(InlineKeyboardButton(text=btn_text, callback_data=callback))
        
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking"))
    return builder.as_markup()

def get_booking_calendar(prefix: str, selected_date: str = None) -> InlineKeyboardMarkup:
    """Генерує єдину сітку: 5 днів зверху та всі 12 годин (по 10 хв) знизу"""
    from datetime import datetime, timedelta
    builder = InlineKeyboardBuilder()
    
    # 1. Ряд дат (5 днів)
    dates_row = []
    now = datetime.now()
    if not selected_date:
        selected_date = now.strftime("%d%m")
        
    for i in range(5):
        dt = now + timedelta(days=i)
        d_str = dt.strftime("%d%m")
        label = dt.strftime("%d.%m")
        if d_str == selected_date:
            label = f"📍 {label}"
        dates_row.append(InlineKeyboardButton(text=label, callback_data=f"{prefix}_date_{d_str}"))
    builder.row(*dates_row)
    
    # 2. Сітка часу (08:00 - 20:00, кожні 10 хв)
    # Зручна структура: Година і ряд кнопок з хвилинами
    for h in range(8, 21):
        hour_str = f"{h:02d}"
        row = []
        for m in range(0, 60, 10):
            t_str = f"{hour_str}:{m:02d}"
            row.append(InlineKeyboardButton(text=t_str, callback_data=f"{prefix}_time_{selected_date}_{hour_str}{m:02d}"))
        builder.row(*row)
        
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking"))
    return builder.as_markup()
