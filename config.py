# config.py
import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "dev").lower()
IS_PROD = ENV == "prod"

if IS_PROD:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_PROD")
    SUPABASE_URL = os.getenv("SUPABASE_URL_PROD")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY_PROD")
else:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_DEV")
    SUPABASE_URL = os.getenv("SUPABASE_URL_DEV")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY_DEV")