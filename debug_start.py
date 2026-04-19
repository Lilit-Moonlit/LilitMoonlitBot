import sys
print("STEP 1: Script started", flush=True)

import os
print("STEP 2: OS imported", flush=True)

try:
    from dotenv import load_dotenv
    print("STEP 3: Dotenv imported", flush=True)
    load_dotenv()
    print("STEP 4: Dotenv loaded", flush=True)

    from app.config import BOT_TOKEN
    print(f"STEP 5: Config loaded. Token prefix: {BOT_TOKEN[:5]}", flush=True)
    
    import aiogram
    print(f"STEP 6: Aiogram imported. Version: {aiogram.__version__}", flush=True)

    print("--- SUCCESS ---", flush=True)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
