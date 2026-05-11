import httpx
import logging
import asyncio
from app.config import (
    META_ACCESS_TOKEN,
    FB_PAGE_ID_MODELS, FB_PAGE_ID_VACANCIES,
    IG_BUSINESS_ACCOUNT_ID_MODELS, IG_BUSINESS_ACCOUNT_ID_VACANCIES,
    BOT_TOKEN,
    ENABLE_SOCIAL_POSTING
)

logger = logging.getLogger(__name__)

class SocialPoster:
    def __init__(self):
        self.access_token = META_ACCESS_TOKEN
        self.base_url = "https://graph.facebook.com/v21.0"

    async def post_to_facebook(self, message: str, page_id: str, media_url: str = None, is_video: bool = False):
        """Premium feature – Facebook cross‑posting is disabled in the free version.
        Returns None and logs a warning.
        """
        from app.config import ENABLE_SOCIAL_POSTING
        if not ENABLE_SOCIAL_POSTING:
            logger.warning("Facebook cross‑posting is disabled (premium feature).")
            return None
        # Original implementation retained for future premium enablement
        if not page_id or not self.access_token:
            logger.warning("Facebook posting skipped: Credentials missing in .env")
            return None
        async with httpx.AsyncClient() as client:
            try:
                if media_url:
                    if is_video:
                        url = f"{self.base_url}/{page_id}/videos"
                        params = {"description": message, "file_url": media_url, "access_token": self.access_token}
                    else:
                        url = f"{self.base_url}/{page_id}/photos"
                        params = {"url": media_url, "caption": message, "access_token": self.access_token}
                else:
                    url = f"{self.base_url}/{page_id}/feed"
                    params = {"message": message, "access_token": self.access_token}
                response = await client.post(url, params=params, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                logger.info(f"✅ Успішно опубліковано у Facebook ({page_id}): {result.get('id')}")
                return {"success": True, "id": result.get('id')}
            except Exception as e:
                error_msg = str(e)
                if hasattr(e, 'response'):
                    try:
                        error_details = e.response.json()
                        error_msg = error_details.get("error", {}).get("message", error_msg)
                    except:
                        error_msg = e.response.text
                logger.error(f"❌ Помилка при публікації у Facebook ({page_id}): {error_msg}")
                return {"success": False, "error": error_msg}
        """
        Публікує пост на стіну сторінки Facebook.
        """
        if not page_id or not self.access_token:
            logger.warning("Facebook posting skipped: Credentials missing in .env")
            return None

        async with httpx.AsyncClient() as client:
            try:
                if media_url:
                    if is_video:
                        # Відео для Facebook
                        url = f"{self.base_url}/{page_id}/videos"
                        params = {
                            "description": message,
                            "file_url": media_url,
                            "access_token": self.access_token
                        }
                    else:
                        # Фото для Facebook
                        url = f"{self.base_url}/{page_id}/photos"
                        params = {
                            "url": media_url,
                            "caption": message,
                            "access_token": self.access_token
                        }
                else:
                    # Тільки текст
                    url = f"{self.base_url}/{page_id}/feed"
                    params = {
                        "message": message,
                        "access_token": self.access_token
                    }

                response = await client.post(url, params=params, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                logger.info(f"✅ Успішно опубліковано у Facebook ({page_id}): {result.get('id')}")
                return {"success": True, "id": result.get('id')}
            except Exception as e:
                error_msg = str(e)
                if hasattr(e, 'response'):
                    try:
                        error_details = e.response.json()
                        error_msg = error_details.get("error", {}).get("message", error_msg)
                    except:
                        error_msg = e.response.text
                
                logger.error(f"❌ Помилка при публікації у Facebook ({page_id}): {error_msg}")
                return {"success": False, "error": error_msg}

    async def post_to_instagram(self, caption: str, user_id: str, media_url: str, is_video: bool = False):
        """Premium feature – Instagram cross‑posting is disabled in the free version.
        Returns None and logs a warning.
        """
        from app.config import ENABLE_SOCIAL_POSTING
        if not ENABLE_SOCIAL_POSTING:
            logger.warning("Instagram cross‑posting is disabled (premium feature).")
            return None
        # Original implementation retained for future premium enablement
        if not user_id or not self.access_token:
            logger.warning("Instagram posting skipped: Credentials missing in .env")
            return None
        async with httpx.AsyncClient() as client:
            try:
                container_url = f"{self.base_url}/{user_id}/media"
                container_params = {"caption": caption, "access_token": self.access_token}
                if is_video:
                    container_params["media_type"] = "REELS"
                    container_params["video_url"] = media_url
                else:
                    container_params["image_url"] = media_url
                response = await client.post(container_url, params=container_params, timeout=30.0)
                response.raise_for_status()
                creation_id = response.json().get("id")
                if is_video:
                    logger.info(f"⏳ Очікування обробки відео Instagram ({creation_id})...")
                    status_url = f"{self.base_url}/{creation_id}"
                    status_params = {"fields": "status_code", "access_token": self.access_token}
                    for _ in range(20):
                        await asyncio.sleep(5)
                        status_resp = await client.get(status_url, params=status_params)
                        status_resp.raise_for_status()
                        status_code = status_resp.json().get("status_code")
                        if status_code == "FINISHED":
                            break
                        elif status_code == "ERROR":
                            raise Exception("Instagram video processing failed (status: ERROR)")
                    else:
                        raise Exception("Instagram video processing timeout")
                publish_url = f"{self.base_url}/{user_id}/media_publish"
                publish_params = {"creation_id": creation_id, "access_token": self.access_token}
                response = await client.post(publish_url, params=publish_params, timeout=30.0)
                response.raise_for_status()
                result = response.json()
                logger.info(f"✅ Успішно опубліковано в Instagram ({user_id}): {result.get('id')}")
                return {"success": True, "id": result.get('id')}
            except Exception as e:
                error_msg = str(e)
                if hasattr(e, 'response'):
                    try:
                        error_details = e.response.json()
                        error_msg = error_details.get("error", {}).get("message", error_msg)
                    except:
                        error_msg = e.response.text
                logger.error(f"❌ Помилка при публікації в Instagram ({user_id}): {error_msg}")
                return {"success": False, "error": error_msg}
        """
        Публікує пост в Instagram Business account.
        Для відео використовується media_type=REELS та очікування обробки.
        """
        if not user_id or not self.access_token:
            logger.warning("Instagram posting skipped: Credentials missing in .env")
            return None

        async with httpx.AsyncClient() as client:
            try:
                # Крок 1: Створення медіа-контейнера
                container_url = f"{self.base_url}/{user_id}/media"
                container_params = {
                    "caption": caption,
                    "access_token": self.access_token
                }
                
                if is_video:
                    container_params["media_type"] = "REELS"
                    container_params["video_url"] = media_url
                else:
                    container_params["image_url"] = media_url
                
                response = await client.post(container_url, params=container_params, timeout=30.0)
                response.raise_for_status()
                creation_id = response.json().get("id")

                # Крок 2: Для відео потрібно дочекатися завершення обробки Instagram
                if is_video:
                    logger.info(f"⏳ Очікування обробки відео Instagram ({creation_id})...")
                    status_url = f"{self.base_url}/{creation_id}"
                    status_params = {
                        "fields": "status_code",
                        "access_token": self.access_token
                    }
                    
                    for _ in range(20): # До 100 секунд
                        await asyncio.sleep(5)
                        status_resp = await client.get(status_url, params=status_params)
                        status_resp.raise_for_status()
                        status_code = status_resp.json().get("status_code")
                        if status_code == "FINISHED":
                            break
                        elif status_code == "ERROR":
                            raise Exception("Instagram video processing failed (status: ERROR)")
                    else:
                        raise Exception("Instagram video processing timeout")

                # Крок 3: Публікація контейнера
                publish_url = f"{self.base_url}/{user_id}/media_publish"
                publish_params = {
                    "creation_id": creation_id,
                    "access_token": self.access_token
                }
                
                response = await client.post(publish_url, params=publish_params, timeout=30.0)
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"✅ Успішно опубліковано в Instagram ({user_id}): {result.get('id')}")
                return {"success": True, "id": result.get('id')}
            except Exception as e:
                error_msg = str(e)
                if hasattr(e, 'response'):
                    try:
                        error_details = e.response.json()
                        error_msg = error_details.get("error", {}).get("message", error_msg)
                    except:
                        error_msg = e.response.text

                logger.error(f"❌ Помилка при публікації в Instagram ({user_id}): {error_msg}")
                return {"success": False, "error": error_msg}

    @staticmethod
    def get_telegram_file_url(file_path: str):
        """Конструює пряме посилання на файл у Telegram для Meta API."""
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
