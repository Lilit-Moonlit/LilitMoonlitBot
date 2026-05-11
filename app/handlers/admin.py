from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.config import ADMIN_USERNAMES
from app.database import dal

admin_router = Router()

def is_admin(username: str) -> bool:
    return username and username.lower() in [u.lower().strip() for u in ADMIN_USERNAMES]

@admin_router.callback_query(F.data.startswith("admin_approve_"))
async def process_admin_approve(callback: CallbackQuery):
    if not is_admin(callback.from_user.username):
        await callback.answer("У вас немає прав адміністратора.", show_alert=True)
        return
        
    proposal_id = int(callback.data.split("_")[-1])
    service = await dal.approve_service_proposal(proposal_id)
    
    if service:
        await callback.message.edit_text(f"✅ Послугу '{service.name}' схвалено та додано в загальну базу!")
    else:
        await callback.message.edit_text("❌ Помилка: пропозицію не знайдено.")
    await callback.answer()

@admin_router.callback_query(F.data.startswith("admin_reject_"))
async def process_admin_reject(callback: CallbackQuery):
    if not is_admin(callback.from_user.username):
        await callback.answer("У вас немає прав адміністратора.", show_alert=True)
        return
        
    proposal_id = int(callback.data.split("_")[-1])
    # Тут можна додати логіку видалення або зміни статусу на rejected
    # Для простоти поки просто повідомлення
    await callback.message.edit_text("❌ Послугу відхилено.")
    await callback.answer()
