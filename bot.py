import os
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands, Intents, Interaction
# bot.py
from config import DISCORD_TOKEN, IS_PROD


# Load environment variables early
load_dotenv()

# Validate required environment variables
required_env_vars = ["GUILD_ID"]
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

GUILD_ID = int(os.getenv("GUILD_ID"))
GUILD_ID_2 = int(os.getenv("GUILD_ID_2"))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("game-night-bot")

# Bot intents
intents = Intents.default()
intents.message_content = True  # Only enable if you need to read message content (e.g., for moderation or manual commands)

bot = commands.Bot(command_prefix="!", intents=intents)

# -- Slash Command Handlers --
from commands.find_game import handle_find_game
from commands.add_game import handle_add_game
from commands.my_games import handle_my_games
from commands.remove_game import handle_remove_game
from commands.register_user import handle_register_user
from commands.create_session import handle_create_session
from commands.list_sessions import handle_list_sessions
from commands.game_info import handle_game_info
from commands.add_session_users import handle_add_session_users
from commands.add_winners import handle_add_session_winners

@bot.event
async def on_ready():
    try:
        if IS_PROD:
            print("In production, syncing all commands.")
            await bot.tree.sync()
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        logger.info(f"🤖 Logged in as {bot.user} | Synced commands to guild {GUILD_ID}")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

# Register commands with guild scoping
@bot.tree.command(name="who_game", description="Find out who owns a game", guilds=[discord.Object(id=GUILD_ID), discord.Object(id=GUILD_ID_2)])
@app_commands.describe(game="The name of the game to search")
async def who_game(interaction: Interaction, game: str):
    await handle_find_game(interaction, game)

@bot.tree.command(name="add_game", description="Search and add a board game from BGG", guilds=[discord.Object(id=GUILD_ID), discord.Object(id=GUILD_ID_2)])
@app_commands.describe(query="The name of the game to search")
async def add_game(interaction: Interaction, query: str):
    await handle_add_game(interaction, query)

@bot.tree.command(name="owned_games", description="Show your board game collection", guilds=[discord.Object(id=GUILD_ID), discord.Object(id=GUILD_ID_2)])
async def owned_games(interaction: Interaction,  user: discord.User = None):
    await handle_my_games(interaction, user)

@bot.tree.command(name="remove_game", description="Remove a game from your collection", guilds=[discord.Object(id=GUILD_ID), discord.Object(id=GUILD_ID_2)])
@app_commands.describe(query="The name of the game to search")
async def remove_game(interaction: Interaction, query: str):
    await handle_remove_game(interaction, query)

@bot.tree.command(name="register_user", description="Register yourself in the game database", guilds=[discord.Object(id=GUILD_ID), discord.Object(id=GUILD_ID_2)])
@app_commands.describe(nickname="Optional nickname to display")
async def register_user(interaction: Interaction, nickname: str = ""):
    await handle_register_user(interaction, nickname)

@bot.tree.command(name="create_session", description="Log a session for a game", guilds=[discord.Object(id=GUILD_ID), discord.Object(id=GUILD_ID_2)])
@app_commands.describe(
    game="Name of the game",
    session_name="Optional name for the session",
    session_date="Date of the session (YYYY-MM-DD)"
)
async def create_session(interaction: Interaction, game: str, session_name: str = "", session_date: str = ""):
    await handle_create_session(interaction, game, session_name or None, session_date or None)

@bot.tree.command(name="list_sessions", description="List sessions for a game", guilds=[discord.Object(id=GUILD_ID), discord.Object(id=GUILD_ID_2)])
@app_commands.describe(game="Name of the game")
async def list_sessions(interaction: Interaction, game: str):
    await handle_list_sessions(interaction, game)

@bot.tree.command(name="game_info", description="View game details from BGG", guilds=[discord.Object(id=GUILD_ID), discord.Object(id=GUILD_ID_2)])
@app_commands.describe(query="The name of the game to search")
async def game_info(interaction: Interaction, query: str):
    await handle_game_info(interaction, query)

@bot.tree.command(name="add_session_users", description="Add users to an existing session", guilds=[discord.Object(id=GUILD_ID), discord.Object(id=GUILD_ID_2)])
@app_commands.describe(session_id="ID of the session")
async def add_session_users(interaction: Interaction, session_id: int):
    await handle_add_session_users(interaction, session_id)

@bot.tree.command(name="add_winner", description="Add winners to a session", guilds=[discord.Object(id=GUILD_ID), discord.Object(id=GUILD_ID_2)])
@app_commands.describe(session_id="ID of the session")
async def add_winner(interaction: Interaction, session_id: int):
    await handle_add_session_winners(interaction, session_id)

# Safely start the bot
try:
    bot.run(DISCORD_TOKEN)
except Exception as e:
    logger.critical(f"Bot failed to start: {e}")
