from typing import Any, Awaitable, Callable, Dict
import time
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.7):
        """
        :param limit: Мінімальний час між запитами від одного користувача (в секундах)
        """
        self.limit = limit
        self.last_user_time: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        user_id = user.id
        now = time.time()

        # НЕ застосовуємо Anti-Flood для альбомів та медіа-файлів
        is_media = False
        if isinstance(event, Message):
            if event.media_group_id or event.photo or event.video or event.animation or event.document:
                is_media = True
        
        if not is_media and user_id in self.last_user_time:
            delta = now - self.last_user_time[user_id]
            if delta < self.limit:
                # Ігноруємо занадто швидке повторне натискання (тільки для тексту/кнопок)
                return

        self.last_user_time[user_id] = now
        return await handler(event, data)
