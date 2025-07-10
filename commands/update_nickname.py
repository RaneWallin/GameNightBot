# commands/update_nickname.py

from discord import Interaction
from helpers.supa_helpers import get_user_by_discord_id, update_user

async def handle_update_nickname(interaction: Interaction, nickname: str):
    await interaction.response.defer(ephemeral=True)

    db_user = get_user_by_discord_id(interaction.user.id, interaction.guild_id)
    if not db_user:
        await interaction.followup.send("❌ You are not registered. Use `/register_user` first.", ephemeral=True)
        return

    try:
        update_user(db_user["id"], {"nickname": nickname})
        await interaction.followup.send(f"✅ Nickname updated to **{nickname}**!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to update nickname: `{str(e)}`", ephemeral=True)
