# register_user.py

from discord import Interaction
from helpers.supa_helpers import get_user_by_discord_id, create_user, register_user_to_server

async def handle_register_user(interaction: Interaction, nickname: str):
    user_id = None

    await interaction.response.defer(ephemeral=True)
    discord_id = int(interaction.user.id)
    username = str(interaction.user)
    server_id = int(interaction.guild_id)

    user = get_user_by_discord_id(discord_id)

    if not user:
        user = create_user(discord_id, username, nickname)

    if user:
        registered = register_user_to_server(user["id"], server_id)
    else:
        await interaction.followup.send("❌ Registration failed. Please try again later or contact support.", ephemeral=True)
        return

    if registered:
        await interaction.followup.send("✅ Registration successful! You can now add and track games.", ephemeral=True)
    else:
        await interaction.followup.send("❌ Registration failed. Please try again later or contact support.", ephemeral=True)
