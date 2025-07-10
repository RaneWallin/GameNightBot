import discord
from discord import Interaction, ui
from helpers.supa_helpers import (
    get_session_by_id,
    get_game_by_id,
    get_winners_in_session,
    get_users_by_ids,
    delete_session_by_id,
)

class ConfirmDeleteView(ui.View):
    def __init__(self, session_id: int):
        super().__init__(timeout=60)
        self.session_id = session_id

        self.add_item(ui.Button(label="❌ Cancel", style=discord.ButtonStyle.secondary, row=0, custom_id="cancel"))
        self.add_item(DeleteButton(session_id))

    async def interaction_check(self, interaction: Interaction):
        return True  # Optionally check permissions

class DeleteButton(ui.Button):
    def __init__(self, session_id: int):
        super().__init__(label="🗑 Confirm Delete", style=discord.ButtonStyle.danger, row=0, custom_id="confirm_delete")
        self.session_id = session_id

    async def callback(self, interaction: Interaction):
        try:
            delete_session_by_id(self.session_id)
            await interaction.response.edit_message(content="✅ Session deleted.", view=None)
        except Exception as e:
            await interaction.response.edit_message(content=f"❌ Failed to delete session: {str(e)}", view=None)

async def handle_delete_session(interaction: Interaction, session_id: int):
    await interaction.response.defer(ephemeral=True)

    session = get_session_by_id(session_id)
    if not session:
        await interaction.followup.send("❌ Session not found.", ephemeral=True)
        return

    game = get_game_by_id(session["game_id"])
    winners = get_winners_in_session(session_id)
    users = get_users_by_ids(winners)
    winner_names = ", ".join([u["nickname"] or u["username"] for u in users]) if users else "None selected"

    content = (
        f"🗓 **Session Info**\n"
        f"• Game: **{game['name']}**\n"
        f"• Date: **{session.get('date', 'Not specified')}**\n"
        f"• Name: **{session.get('name') or '(no name)'}**\n"
        f"• Winners: {winner_names}\n\n"
        f"Are you sure you want to delete this session?"
    )

    view = ConfirmDeleteView(session_id)
    await interaction.followup.send(content, view=view, ephemeral=True)
