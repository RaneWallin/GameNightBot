# register_user.py
from discord import Interaction
from supabase import Client
from helpers.supa_helpers import get_user_by_discord_id, create_user

async def handle_register_user(interaction: Interaction, nickname: str):
    await interaction.response.defer(ephemeral=True)
    discord_id = int(interaction.user.id)

    # Check if the user already exists
    user_data = get_user_by_discord_id(discord_id)
    if user_data:
        await interaction.followup.send("ℹ️ You are already registered.", ephemeral=True)
        return

    # Create the user
    result = create_user(discord_id, str(interaction.user), nickname)
    if result:
        await interaction.followup.send("✅ You have been registered successfully!", ephemeral=True)
    else:
        await interaction.followup.send("❌ Something went wrong while registering.", ephemeral=True)
