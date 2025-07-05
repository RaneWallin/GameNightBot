# register_user.py

from discord import Interaction
from helpers.supa_helpers import get_user_by_discord_id, create_user

async def handle_register_user(interaction: Interaction, nickname: str):
    await interaction.response.defer(ephemeral=True)
    discord_id = int(interaction.user.id)
    username = str(interaction.user)

    existing_user = get_user_by_discord_id(discord_id)
    if existing_user:
        await interaction.followup.send("ℹ️ You're already registered in the system.", ephemeral=True)
        return

    success = create_user(discord_id, username, nickname)
    if success:
        await interaction.followup.send("✅ Registration successful! You can now add and track games.", ephemeral=True)
    else:
        await interaction.followup.send("❌ Registration failed. Please try again later or contact support.", ephemeral=True)
