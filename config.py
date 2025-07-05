# config.py
import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "dev").lower()
IS_PROD = ENV == "prod"

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_PROD") if IS_PROD else os.getenv("DISCORD_TOKEN_DEV")
GUILD_ID = int(os.getenv("GUILD_ID_PROD") if IS_PROD else os.getenv("GUILD_ID_DEV"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
