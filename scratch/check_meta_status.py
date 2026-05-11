import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FB_PAGES = {
    "Models": os.getenv("FB_PAGE_ID_MODELS"),
    "Vacancies": os.getenv("FB_PAGE_ID_VACANCIES")
}
IG_ACCOUNTS = {
    "Models": os.getenv("IG_BUSINESS_ACCOUNT_ID_MODELS"),
    "Vacancies": os.getenv("IG_BUSINESS_ACCOUNT_ID_VACANCIES")
}

async def check_token():
    print("--- Token Check ---")
    if not META_ACCESS_TOKEN:
        print("X META_ACCESS_TOKEN missing in .env")
        return False
    
    async with httpx.AsyncClient() as client:
        # Перевірка самого токена (інформація про власника)
        url = "https://graph.facebook.com/v21.0/me"
        params = {"access_token": META_ACCESS_TOKEN}
        try:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                print(f"OK: Token is active. User: {data.get('name')} (ID: {data.get('id')})")
                return True
            else:
                error = resp.json().get("error", {})
                print(f"X Token error: {error.get('message')}")
                return False
        except Exception as e:
            print(f"X Critical error: {e}")
            return False

async def check_pages():
    print("\n--- Facebook Pages Check ---")
    async with httpx.AsyncClient() as client:
        for name, page_id in FB_PAGES.items():
            if not page_id:
                print(f"! Page ID '{name}' not specified")
                continue
            
            url = f"https://graph.facebook.com/v21.0/{page_id}"
            params = {"fields": "name,is_published", "access_token": META_ACCESS_TOKEN}
            try:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    status = "Published" if data.get("is_published") else "NOT Published"
                    print(f"OK: Page '{name}' ({data.get('name')}): {status}. Access granted.")
                else:
                    error = resp.json().get("error", {})
                    print(f"X Page '{name}' (ID: {page_id}): {error.get('message')}")
            except Exception as e:
                print(f"X Error checking page '{name}': {e}")

async def check_instagram():
    print("\n--- Instagram Business Check ---")
    async with httpx.AsyncClient() as client:
        for name, ig_id in IG_ACCOUNTS.items():
            if not ig_id:
                print(f"! Instagram ID '{name}' not specified")
                continue
            
            url = f"https://graph.facebook.com/v21.0/{ig_id}"
            params = {"fields": "username,name", "access_token": META_ACCESS_TOKEN}
            try:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"OK: Instagram '{name}' (@{data.get('username')}): Active.")
                else:
                    error = resp.json().get("error", {})
                    print(f"X Instagram '{name}' (ID: {ig_id}): {error.get('message')}")
            except Exception as e:
                print(f"X Error checking Instagram '{name}': {e}")

async def main():
    if await check_token():
        await check_pages()
        await check_instagram()

if __name__ == "__main__":
    asyncio.run(main())
