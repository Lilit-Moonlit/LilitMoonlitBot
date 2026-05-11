import asyncio
from typing import Any, Awaitable, Callable, Dict, List
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

class AlbumMiddleware(BaseMiddleware):
    """
    Middleware для групування медіа-груп (альбомів) в один об'єкт.
    Додає список 'album' у data.
    """
    def __init__(self, latency: float = 0.1):
        self.latency = latency
        self.album_data: Dict[str, List[Message]] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message) or not event.media_group_id:
            return await handler(event, data)

        try:
            self.album_data[event.media_group_id].append(event)
            return # Очікуємо наступні частини альбому
        except KeyError:
            self.album_data[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)

            data["album"] = self.album_data.pop(event.media_group_id)
            return await handler(event, data)
