# helpers/command_register.py
import discord
from config import IS_PROD, GUILD_ID

def guilded_command(name, description):
    if IS_PROD:
        return lambda func: discord.app_commands.command(name=name, description=description)(func)
    else:
        return lambda func: discord.app_commands.command(name=name, description=description, guild=discord.Object(id=GUILD_ID))(func)
