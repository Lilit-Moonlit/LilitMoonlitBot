from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters import StateFilter
import asyncio
import logging

logger = logging.getLogger(__name__)

from app.states.ads import AdStates, QuickAdStates
from app.utils.ads_templates import MODEL_FIELDS, VACANCY_FIELDS, format_ad_post
from app.config import (
    VACANCY_CHANNEL_ID, MODEL_CHANNEL_ID,
    FB_PAGE_ID_MODELS, FB_PAGE_ID_VACANCIES,
    IG_BUSINESS_ACCOUNT_ID_MODELS, IG_BUSINESS_ACCOUNT_ID_VACANCIES,
    BOT_TOKEN
)
from app.database import dal
from app.database.models import RoleEnum, SocialPostQueue
from app.states.master_profile import MasterProfileStates

ads_router = Router()

# Список всіх головних кнопок для швидкої перевірки
MAIN_MENU_BUTTONS = [
    "🔎 Знайти майстра", "💼 Я майстер",
    "💅 Шукаю модель", "📢 Вакансії",
    "⬆️Додати оголошення⬆️",
    "📅 Мої записи", "🏰 Спільнота", "🔄 /start"
]

def get_cancel_kb(with_skip=False):
    builder = ReplyKeyboardBuilder()
    if with_skip:
        builder.row(types.KeyboardButton(text="Пропустити ⏭️"))
    builder.row(types.KeyboardButton(text="❌ Скасувати"))
    return builder.as_markup(resize_keyboard=True)

def get_preview_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Опублікувати", callback_data="publish_ad"))
    builder.row(InlineKeyboardButton(text="🔄 Заповнити заново", callback_data="restart_ad"))
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_ad"))
    return builder.as_markup()

def get_channel_post_kb(ad_type: str):
    bot_link = "https://t.me/LilitMoonlitBot"
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💎 Наші ресурси", url=bot_link))
    return builder.as_markup()

# --- Вспоміжна функція для скидання стану при натисканні меню ---
async def check_menu_click(message: Message, state: FSMContext):
    if message.text in MAIN_MENU_BUTTONS:
        await state.clear()
        return True
    return False

# --- View Handlers (Канали) ---
@ads_router.message(F.text == "💅 Шукаю модель")
async def view_models_channel(message: Message, state: FSMContext):
    await state.clear()
    text = "💅 <b>Канал пошуку моделей</b>\n\nТут ви знайдете актуальні пропозиції від майстрів."
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Перейти в канал 💅", url="https://t.me/LilitModel"))
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@ads_router.message(F.text == "📢 Вакансії")
async def view_vacancies_channel(message: Message, state: FSMContext):
    await state.clear()
    text = "📢 <b>Канал вакансій</b>\n\nТут зібрані найкращі пропозиції роботи."
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Перейти в канал 📢", url="https://t.me/LilitVacancy"))
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

# --- Об'єднане меню "Додати оголошення" ---
@ads_router.message(F.text.contains("Додати оголошення"))
async def start_ad_selection(message: Message, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🚀 Швидкий режим (текст + медіа)", callback_data="choose_quick_ad"))
    builder.row(InlineKeyboardButton(text="💃 Знайти модель (покроково)", callback_data="choose_ad_model"))
    builder.row(InlineKeyboardButton(text="📢 Додати вакансію (покроково)", callback_data="choose_ad_vacancy"))
    await message.answer("Яким способом ви хочете створити оголошення?", reply_markup=builder.as_markup())

# --- Швидкий режим ---
@ads_router.callback_query(F.data == "choose_quick_ad")
async def start_quick_ad(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💃 Шукаю модель", callback_data="quick_type_model"))
    builder.row(InlineKeyboardButton(text="📢 Вакансія", callback_data="quick_type_vacancy"))
    await callback.message.edit_text("Оберіть тип оголошення для швидкого режиму:", reply_markup=builder.as_markup())

@ads_router.callback_query(F.data.startswith("quick_type_"))
async def process_quick_type(callback: CallbackQuery, state: FSMContext):
    ad_type = callback.data.replace("quick_type_", "")
    await state.update_data(ad_type=ad_type, is_quick=True)
    await state.set_state(QuickAdStates.waiting_for_content)
    
    if ad_type == "model":
        text = (
            "🚀 <b>Швидкий режим: Шукаю модель</b>\n\n"
            "Надішліть текст оголошення разом з фото вашої роботи або відео.\n\n"
            "<i>Порада: вкажіть послугу, дату/час, ціну, район та <b>контакти</b>.</i>"
        )
    else:
        text = (
            "🚀 <b>Швидкий режим: Вакансія</b>\n\n"
            "Надішліть текст вакансії разом з фото салону або відео робочого місця.\n\n"
            "<i>Порада: вкажіть посаду, графік, зарплату, вимоги та <b>контакти</b>.</i>"
        )
    
    await callback.message.edit_text(text, parse_mode="HTML")

@ads_router.message(QuickAdStates.waiting_for_content)
async def process_quick_content(message: Message, state: FSMContext, album: list[Message] = None):
    if await check_menu_click(message, state): return
    
    # Якщо це альбом, шукаємо підпис у будь-якому з повідомлень
    text = None
    photos = []
    videos = []
    
    messages = album if album else [message]
    
    for msg in messages:
        if msg.caption and not text:
            text = msg.caption
        if msg.photo:
            photos.append(msg.photo[-1].file_id)
        elif msg.video or msg.animation:
            videos.append((msg.video or msg.animation).file_id)
            
    # Якщо це не альбом, а просто текстове повідомлення
    if not text and message.text:
        text = message.text

    if not text:
        await message.answer("⚠️ Будь ласка, додайте опис (текст) до вашого оголошення.")
        return

    await state.update_data(
        quick_text=text,
        quick_photos=photos,
        quick_videos=videos
    )
    
    await state.set_state(QuickAdStates.preview)
    
    # Попередній перегляд
    await message.answer("👀 <b>Попередній перегляд швидкого оголошення:</b>", parse_mode="HTML")
    
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="✅ Опублікувати", callback_data="publish_quick_ad"))
    kb.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_ad"))
    
    if photos or videos:
        from aiogram.types import InputMediaPhoto, InputMediaVideo
        media = []
        for v in videos:
            media.append(InputMediaVideo(media=v))
        for p in photos:
            media.append(InputMediaPhoto(media=p))
        
        if media:
            media[0].caption = text
            media[0].parse_mode = "HTML"
            
            if len(media) > 1:
                await message.answer_media_group(media=media)
                await message.answer("Вище ваше оголошення. Опублікувати?", reply_markup=kb.as_markup())
            else:
                if isinstance(media[0], InputMediaVideo):
                    await message.answer_video(media[0].media, caption=text, reply_markup=kb.as_markup(), parse_mode="HTML")
                else:
                    await message.answer_photo(media[0].media, caption=text, reply_markup=kb.as_markup(), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@ads_router.callback_query(F.data == "publish_quick_ad", QuickAdStates.preview)
async def publish_quick_ad_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ad_type = data.get("ad_type")
    text = data.get("quick_text")
    photos = data.get("quick_photos", [])
    videos = data.get("quick_videos", [])
    
    channel = MODEL_CHANNEL_ID if ad_type == "model" else VACANCY_CHANNEL_ID
    
    try:
        # 1. Публікація в Telegram
        if photos or videos:
            from aiogram.types import InputMediaPhoto, InputMediaVideo
            media = []
            for v in videos:
                media.append(InputMediaVideo(media=v))
            for p in photos:
                media.append(InputMediaPhoto(media=p))
                
            if media:
                media[0].caption = text
                media[0].parse_mode = "HTML"
                
                if len(media) > 1:
                    await callback.bot.send_media_group(chat_id=channel, media=media)
                else:
                    if isinstance(media[0], InputMediaVideo):
                        await callback.bot.send_video(channel, video=media[0].media, caption=text, parse_mode="HTML")
                    else:
                        await callback.bot.send_photo(channel, photo=media[0].media, caption=text, parse_mode="HTML")

                await callback.bot.send_message(channel, ".", reply_markup=get_channel_post_kb(ad_type))
        else:
            await callback.bot.send_message(channel, text=text, reply_markup=get_channel_post_kb(ad_type))
            
        await callback.message.answer("✅ <b>Успішно опубліковано в Telegram!</b>\n\nКрос-постинг у Facebook/Instagram додано в чергу та з'явиться там згодом.", parse_mode="HTML")
        
        # 2. Додавання в чергу для Meta (беремо найкраще медіа: відео в пріоритеті)
        meta_media_id = None
        meta_media_type = None
        if videos:
            meta_media_id = videos[0]
            meta_media_type = "video"
        elif photos:
            meta_media_id = photos[0]
            meta_media_type = "photo"
            
        await dal.add_to_post_queue(
            ad_type=ad_type,
            text=text,
            media_file_id=meta_media_id,
            media_type=meta_media_type
        )
        
        await state.clear()
        
        # --- Автоматична реєстрація майстра ---
        user_id = callback.from_user.id
        master = await dal.get_master(user_id)
        
        if not master:
            from app.database.models import RoleEnum
            from app.states.master_profile import MasterProfileStates
            await dal.update_user_role(user_id, RoleEnum.MASTER)
            await dal.create_master(user_id=user_id, description=f"Швидке оголошення: {text[:100]}...")
            
            await state.set_state(MasterProfileStates.choosing_service_category)
            services = await dal.get_all_services()
            await state.update_data(selected_services=[])
            
            from app.keyboards.inline import get_categories_keyboard
            await callback.message.answer(
                "🎉 Оголошення опубліковано! Ми автоматично створили вам профіль майстра.\n\n"
                "<b>Важливо:</b> щоб клієнти могли знайти вас через 'Пошук майстра', "
                "будь ласка, оберіть послуги, які ви надаєте:",
                reply_markup=get_categories_keyboard(services, set(), is_master=True),
                parse_mode="HTML"
            )
        else:
            from app.keyboards.main_kb import get_start_keyboard
            await callback.message.answer("🏠 Головне меню:", reply_markup=get_start_keyboard())
        
        try:
            await callback.message.delete()
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error publishing quick ad: {e}")
        await callback.message.answer(f"❌ Помилка: {e}")
        await callback.answer()

@ads_router.callback_query(F.data == "choose_ad_model")
async def start_model_ad_callback(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    await state.clear()
    await state.set_state(AdStates.model_service)
    await state.update_data(ad_type="model")
    await callback.message.answer(MODEL_FIELDS[0]["prompt"], reply_markup=get_cancel_kb())

@ads_router.message(StateFilter(AdStates.model_service, AdStates.model_datetime, AdStates.model_location, 
                               AdStates.model_requirements, AdStates.model_price, AdStates.model_contact, AdStates.model_photo, AdStates.model_video))
async def process_model_fields(message: Message, state: FSMContext, album: list[Message] = None):
    if await check_menu_click(message, state): return
    if message.text == "❌ Скасувати":
        await state.clear()
        from app.keyboards.main_kb import get_start_keyboard
        await message.answer("Скасовано.", reply_markup=get_start_keyboard())
        return

    current_state = await state.get_state()
    for i, f in enumerate(MODEL_FIELDS):
        if current_state == getattr(AdStates, f["key"]).state:
            # Обробка полів (дата тепер вільний текст за запитом користувача)
            if f["key"] == "model_photo":
                data = await state.get_data()
                photos = data.get("model_photos", [])
                videos = data.get("model_videos", [])
                
                messages = album if album else [message]
                
                media_added = False
                for msg in messages:
                    if msg.photo:
                        photos.append(msg.photo[-1].file_id)
                        media_added = True
                    elif msg.video or msg.animation:
                        videos.append((msg.video or msg.animation).file_id)
                        media_added = True
                
                if media_added:
                    await state.update_data(model_photos=photos, model_videos=videos)
                    total = len(photos) + len(videos)
                    
                    if total < 10:
                        kb = InlineKeyboardBuilder()
                        kb.row(InlineKeyboardButton(text="✅ Готово, далі", callback_data="model_photo_done"))
                        await message.answer(f"✅ Додано медіа (всього {total}/10). Можете надіслати ще або натиснути 'Готово':", 
                                           reply_markup=kb.as_markup())
                        return
                    else:
                        val = photos
                elif message.text == "Пропустити ⏭️":
                    val = None
                else:
                    await message.answer("⚠️ Будь ласка, надішліть фото/відео або натисніть 'Пропустити':")
                    return
            elif f["key"] == "model_video":
                data = await state.get_data()
                videos = data.get("model_videos", [])
                
                messages = album if album else [message]
                
                media_added = False
                for msg in messages:
                    if msg.video or msg.animation:
                        videos.append((msg.video or msg.animation).file_id)
                        media_added = True
                    elif msg.photo:
                        # Якщо на етапі відео раптом кинули фото - теж приймаємо
                        photos = data.get("model_photos", [])
                        photos.append(msg.photo[-1].file_id)
                        await state.update_data(model_photos=photos)
                        media_added = True

                if media_added:
                    await state.update_data(model_videos=videos)
                    await message.answer(f"✅ Додано! Всього медіа: {len(videos) + len(data.get('model_photos', []))}/10")
                    return
                elif message.text == "Пропустити ⏭️":
                    val = videos # Зберігаємо існуючі відео
                else:
                    await message.answer("⚠️ Будь ласка, надішліть відео або натисніть 'Пропустити':")
                    return
            else:
                val = message.text

            await state.update_data({f["key"]: val})
            
            if i + 1 < len(MODEL_FIELDS):
                next_f = MODEL_FIELDS[i+1]
                await state.set_state(getattr(AdStates, next_f["key"]))
                kb = get_cancel_kb(with_skip=("photo" in next_f["key"] or "video" in next_f["key"]))
                await message.answer(next_f["prompt"], reply_markup=kb)
            else:
                await show_ad_preview(message, state, "model")
            break

@ads_router.callback_query(F.data == "model_photo_done", AdStates.model_photo)
async def model_photo_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("model_videos"): # Змінено на videos
        # Якщо відео вже було додано разом з фото, переходимо до превью
        await show_ad_preview(callback.message, state, "model")
    else:
        await state.set_state(AdStates.model_video)
        await callback.message.answer(MODEL_FIELDS[-1]["prompt"], reply_markup=get_cancel_kb(with_skip=True))
    await callback.answer()

async def show_ad_preview(message: Message, state: FSMContext, ad_type: str):
    data = await state.get_data()
    post_text = format_ad_post(data, ad_type)
    photos = data.get(f"{ad_type}_photos", [])
    videos = data.get(f"{ad_type}_videos", [])
    
    await message.answer("👀 <b>Попередній перегляд:</b>", parse_mode="HTML")
    
    if photos or videos:
        from aiogram.types import InputMediaPhoto, InputMediaVideo
        media = []
        
        # Спочатку додаємо відео
        for v in videos:
            media.append(InputMediaVideo(media=v))
        # Потім фото
        for p in photos:
            media.append(InputMediaPhoto(media=p))
        
        if media:
            media[0].caption = post_text
            media[0].parse_mode = "HTML"
            
            if len(media) > 1:
                await message.answer_media_group(media=media)
                await message.answer("Вище ваше медіа-оголошення. Опублікувати?", reply_markup=get_preview_kb())
            else:
                # Одне медіа
                if isinstance(media[0], InputMediaVideo):
                    await message.answer_video(media[0].media, caption=post_text, reply_markup=get_preview_kb(), parse_mode="HTML")
                else:
                    await message.answer_photo(media[0].media, caption=post_text, reply_markup=get_preview_kb(), parse_mode="HTML")
    else:
        await message.answer(post_text, reply_markup=get_preview_kb(), parse_mode="HTML")

# --- Вакансії ---
@ads_router.callback_query(F.data == "choose_ad_vacancy")
async def start_vacancy_ad_callback(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    await state.clear()
    await state.set_state(AdStates.vacancy_position)
    await state.update_data(ad_type="vacancy")
    await callback.message.answer(VACANCY_FIELDS[0]["prompt"], reply_markup=get_cancel_kb())

@ads_router.message(StateFilter(AdStates.vacancy_position, AdStates.vacancy_company, AdStates.vacancy_salary, 
                               AdStates.vacancy_location, AdStates.vacancy_requirements, AdStates.vacancy_contact, AdStates.vacancy_photo, AdStates.vacancy_video))
async def process_vacancy_fields(message: Message, state: FSMContext, album: list[Message] = None):
    if await check_menu_click(message, state): return
    if message.text == "❌ Скасувати":
        await state.clear()
        from app.keyboards.main_kb import get_start_keyboard
        await message.answer("Скасовано.", reply_markup=get_start_keyboard())
        return

    current_state = await state.get_state()
    for i, f in enumerate(VACANCY_FIELDS):
        if current_state == getattr(AdStates, f["key"]).state:
            # Спеціальна обробка фото
            if f["key"] == "vacancy_photo":
                data = await state.get_data()
                photos = data.get("vacancy_photos", [])
                videos = data.get("vacancy_videos", [])
                
                messages = album if album else [message]
                
                media_added = False
                for msg in messages:
                    if msg.photo:
                        photos.append(msg.photo[-1].file_id)
                        media_added = True
                    elif msg.video or msg.animation:
                        videos.append((msg.video or msg.animation).file_id)
                        media_added = True
                
                if media_added:
                    await state.update_data(vacancy_photos=photos, vacancy_videos=videos)
                    total = len(photos) + len(videos)
                    
                    if total < 10:
                        kb = InlineKeyboardBuilder()
                        kb.row(InlineKeyboardButton(text="✅ Готово, далі", callback_data="vacancy_photo_done"))
                        await message.answer(f"✅ Додано медіа (всього {total}/10). Можете надіслати ще або натиснути 'Готово':", 
                                           reply_markup=kb.as_markup())
                        return
                    else:
                        val = photos
                elif message.text == "Пропустити ⏭️":
                    val = None
                else:
                    await message.answer("⚠️ Будь ласка, надішліть фото/відео або натисніть 'Пропустити':")
                    return
            elif f["key"] == "vacancy_video":
                data = await state.get_data()
                videos = data.get("vacancy_videos", [])
                
                messages = album if album else [message]
                
                media_added = False
                for msg in messages:
                    if msg.video or msg.animation:
                        videos.append((msg.video or msg.animation).file_id)
                        media_added = True
                    elif msg.photo:
                        photos = data.get("vacancy_photos", [])
                        photos.append(msg.photo[-1].file_id)
                        await state.update_data(vacancy_photos=photos)
                        media_added = True

                if media_added:
                    await state.update_data(vacancy_videos=videos)
                    await message.answer(f"✅ Додано! Всього медіа: {len(videos) + len(data.get('vacancy_photos', []))}/10")
                    return
                elif message.text == "Пропустити ⏭️":
                    val = videos
                else:
                    await message.answer("⚠️ Будь ласка, надішліть відео або натисніть 'Пропустити':")
                    return
            else:
                val = message.text

            await state.update_data({f["key"]: val})
            
            if i + 1 < len(VACANCY_FIELDS):
                next_f = VACANCY_FIELDS[i+1]
                await state.set_state(getattr(AdStates, next_f["key"]))
                kb = get_cancel_kb(with_skip=("photo" in next_f["key"] or "video" in next_f["key"]))
                await message.answer(next_f["prompt"], reply_markup=kb)
            else:
                await show_ad_preview(message, state, "vacancy")
            break

@ads_router.callback_query(F.data == "vacancy_photo_done", AdStates.vacancy_photo)
async def vacancy_photo_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("vacancy_videos"): # Змінено на videos
        # Якщо відео вже було додано разом з фото, переходимо до превью
        await show_ad_preview(callback.message, state, "vacancy")
    else:
        await state.set_state(AdStates.vacancy_video)
        await callback.message.answer(VACANCY_FIELDS[-1]["prompt"], reply_markup=get_cancel_kb(with_skip=True))
    await callback.answer()

# --- Коллбеки ---
@ads_router.callback_query(F.data == "publish_ad")
async def publish_ad(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    st = await state.get_state()
    is_model = data.get("ad_type") == "model" or "model" in str(st)
    channel = MODEL_CHANNEL_ID if is_model else VACANCY_CHANNEL_ID
    
    # Визначаємо ID для Meta залежно від типу оголошення
    fb_page_id = FB_PAGE_ID_MODELS if is_model else FB_PAGE_ID_VACANCIES
    ig_user_id = IG_BUSINESS_ACCOUNT_ID_MODELS if is_model else IG_BUSINESS_ACCOUNT_ID_VACANCIES
    
    try:
        post_text = format_ad_post(data, "model" if is_model else "vacancy")
        photos = data.get(f"{'model' if is_model else 'vacancy'}_photos", [])
        videos = data.get(f"{'model' if is_model else 'vacancy'}_videos", [])
        
        # --- 1. Публікація в Telegram канал ---
        if photos or videos:
            from aiogram.types import InputMediaPhoto, InputMediaVideo
            media = []
            
            for v in videos:
                media.append(InputMediaVideo(media=v))
            for p in photos:
                media.append(InputMediaPhoto(media=p))
                
            if media:
                media[0].caption = post_text
                media[0].parse_mode = "HTML"
                
                if len(media) > 1:
                    await callback.bot.send_media_group(chat_id=channel, media=media)
                else:
                    # Одне медіа
                    if isinstance(media[0], InputMediaVideo):
                        await callback.bot.send_video(chat_id=channel, video=media[0].media, caption=post_text, parse_mode="HTML")
                    else:
                        await callback.bot.send_photo(chat_id=channel, photo=media[0].media, caption=post_text, parse_mode="HTML")

                await callback.bot.send_message(
                    chat_id=channel, 
                    text=".", 
                    reply_markup=get_channel_post_kb("model" if is_model else "vacancy"),
                    parse_mode="HTML"
                )
        else:
            await callback.bot.send_message(
                chat_id=channel, 
                text=post_text, 
                reply_markup=get_channel_post_kb("model" if is_model else "vacancy"),
                parse_mode="HTML"
            )
            
        await callback.message.answer("✅ <b>Успішно опубліковано в Telegram!</b>", parse_mode="HTML")
        
        # --- 2. Додавання в чергу для Meta ---
        meta_media_id = None
        meta_media_type = None
        if videos:
            meta_media_id = videos[0]
            meta_media_type = "video"
        elif photos:
            meta_media_id = photos[0]
            meta_media_type = "photo"
            
        await dal.add_to_post_queue(
            ad_type="model" if is_model else "vacancy",
            text=post_text,
            media_file_id=meta_media_id,
            media_type=meta_media_type
        )

        try:
            await callback.message.delete()
        except:
            pass
        pass
            
        # --- Автоматична реєстрація майстра ---
        user_id = callback.from_user.id
        master = await dal.get_master(user_id)
        
        if not master:
            # Створюємо профіль майстра
            await dal.update_user_role(user_id, RoleEnum.MASTER)
            
            # Формуємо опис на основі оголошення
            if is_model:
                description = f"Шукаю модель: {data.get('model_service', '')}. {data.get('model_requirements', '')}"
            else:
                description = f"Вакансія: {data.get('vacancy_position', '')} у {data.get('vacancy_company', '')}. {data.get('vacancy_requirements', '')}"
            
            await dal.create_master(user_id=user_id, description=description)
            
            # Спробуємо розпізнати контакт
            contact = data.get('model_contact' if is_model else 'vacancy_contact', "")
            if contact:
                if contact.startswith("@"):
                    await dal.update_master_profile(user_id, telegram=contact)
                elif contact.replace("+", "").isdigit():
                    await dal.update_master_profile(user_id, phone=contact)
            
            await state.set_state(MasterProfileStates.choosing_service_category)
            services = await dal.get_all_services()
            await state.update_data(selected_services=[])
            
            from app.keyboards.inline import get_categories_keyboard
            await callback.message.answer(
                "🎉 Оголошення опубліковано! Ми автоматично створили вам профіль майстра.\n\n"
                "<b>Важливо:</b> щоб клієнти могли знайти вас через 'Пошук майстра', "
                "будь ласка, оберіть послуги, які ви надаєте:",
                reply_markup=get_categories_keyboard(services, set(), is_master=True),
                parse_mode="HTML"
            )
        else:
            await state.clear()
            from app.keyboards.main_kb import get_start_keyboard
            await callback.message.answer("🏠 Головне меню:", reply_markup=get_start_keyboard())
    except Exception as e:
        await callback.message.answer(f"❌ Помилка: {e}\n\n<i>Переконайтеся, що бот є адміністратором каналу та ID вказано правильно.</i>", parse_mode="HTML")

@ads_router.callback_query(F.data == "restart_ad")
async def restart_ad(callback: CallbackQuery, state: FSMContext):
    st = await state.get_state()
    if st and "model" in st:
        await start_model_ad_callback(callback, state)
    else:
        await start_vacancy_ad_callback(callback, state)
    await callback.answer()

@ads_router.callback_query(F.data == "cancel_ad")
async def cancel_ad(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    from app.keyboards.main_kb import get_start_keyboard
    await callback.message.answer("Процес скасовано.", reply_markup=get_start_keyboard())
    await callback.answer()
