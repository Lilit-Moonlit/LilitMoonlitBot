import httpx
import asyncio
from app.config import META_ACCESS_TOKEN

async def debug_token():
    url = "https://graph.facebook.com/debug_token"
    # To debug a token, you need an APP TOKEN (AppID|AppSecret)
    # But we can try to call /me/permissions with the user token
    
    perm_url = "https://graph.facebook.com/v21.0/me/permissions"
    async with httpx.AsyncClient() as client:
        resp = await client.get(perm_url, params={"access_token": META_ACCESS_TOKEN})
        print("Permissions:")
        print(resp.json())
        
        me_url = "https://graph.facebook.com/v21.0/me"
        resp_me = await client.get(me_url, params={"access_token": META_ACCESS_TOKEN})
        print("\nMe:")
        print(resp_me.json())

if __name__ == "__main__":
    asyncio.run(debug_token())
