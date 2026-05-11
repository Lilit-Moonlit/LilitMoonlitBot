import httpx
import asyncio

async def exchange_token():
    print("--- Обмін токена на Long-lived (60 днів) ---")
    
    app_id = input("Введіть App ID: ").strip()
    app_secret = input("Введіть App Secret: ").strip()
    short_token = input("Введіть короткий токен (з Graph API Explorer): ").strip()

    url = "https://graph.facebook.com/v21.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                long_token = data.get("access_token")
                print("\n✅ УСПІХ! Ваш довгий токен (60 днів):")
                print("-" * 50)
                print(long_token)
                print("-" * 50)
                print("\nСкопіюйте його та вставте в .env у поле META_ACCESS_TOKEN")
            else:
                print(f"\n❌ Помилка: {resp.text}")
        except Exception as e:
            print(f"\n❌ Помилка запиту: {e}")

if __name__ == "__main__":
    asyncio.run(exchange_token())
