import os
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents, Interaction, app_commands, ui, ButtonStyle, SelectOption, Member
from typing import Annotated
import discord
from supabase import create_client, Client

from commands.find_game import handle_find_game
from commands.add_game import handle_add_game
from commands.my_games import handle_my_games
from commands.remove_game import handle_remove_game
from commands.register_user import handle_register_user
from commands.create_session import handle_create_session
from commands.list_sessions import handle_list_sessions
from commands.game_info import handle_game_info
from commands.add_session_users import handle_add_session_users



# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define intents
intents = Intents.default()
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)
user_search_cache = {}
user_tasks = {}

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    # Clear guild commands
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))

    print(f"🤖 Logged in as {bot.user.name} | Synced to guild {GUILD_ID}")

@bot.tree.command(name="find_game", description="Find out who owns a game", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(query="The name of the game to search")
async def find_game(interaction: Interaction, query: str):
    await handle_find_game(interaction, query)


@bot.tree.command(name="add_game", description="Search and add a board game from BGG", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(query="The name of the game to search")
async def add_game(interaction: Interaction, query: str):
    await handle_add_game(interaction, query)

@bot.tree.command(name="my_games", description="Show your board game collection", guild=discord.Object(id=GUILD_ID))
async def my_games(interaction: Interaction):
    await handle_my_games(interaction)

@bot.tree.command(name="remove_game", description="Remove a game from your collection", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(query="The name of the game to search")
async def remove_game(interaction: Interaction, query: str):
    await handle_remove_game(interaction, query)

@bot.tree.command(name="register_user", description="Add yourself to the game database", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(nickname="Optional nickname to display instead of your Discord name")
async def register_user(interaction: Interaction, nickname: str = ""):
    await handle_register_user(interaction, nickname)

@bot.tree.command(name="create_session", description="Log a session for a game", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(game="Name of the game", session_name="Optional name for the session", session_date="Date of the session (YYYY-MM-DD)")
async def create_session(interaction: Interaction, game: str, session_name: str = "", session_date: str = ""):
    await handle_create_session(interaction, game, session_name or None, session_date or None)

@bot.tree.command(name="list_sessions", description="List sessions where a game was played", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(game="The name of the game to search")
async def list_sessions(interaction: Interaction, game: str):
    await handle_list_sessions(interaction, game)

@bot.tree.command(name="game_info", description="Look up a board game on BGG", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(query="The name of the game to search")
async def game_info(interaction: Interaction, query: str):
    await handle_game_info(interaction, query)

@bot.tree.command(name="add_session_users", description="Add users to a session from the database", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(session_id="The session ID to add users to")
async def add_session_users(interaction: Interaction, session_id: int):
    await handle_add_session_users(interaction, session_id)



bot.run(DISCORD_TOKEN)
