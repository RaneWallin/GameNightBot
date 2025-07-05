import discord
from discord import Interaction, ui, SelectOption
from helpers.supa_helpers import (
    get_all_registered_users,
    get_users_in_session,
    link_user_to_session,
    get_winners_in_session,
    link_winner_to_session
)

class UserSelect(ui.Select):
    def __init__(self, session_id: int, options: list[SelectOption]):
        self.session_id = session_id
        super().__init__(
            placeholder="Select users to add to this session",
            min_values=1,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: Interaction):
        selected_ids = [int(uid) for uid in self.values]
        added = 0
        failed = 0

        for user_id in selected_ids:
            try:
                link_winner_to_session(self.session_id, user_id)
                added += 1
            except Exception as e:
                failed += 1  # You could log e for debugging

        msg = f"✅ Added {added} winner(s) to the session."
        if failed > 0:
            msg += f" ⚠️ Failed to add {failed} user(s)."

        await interaction.response.edit_message(
            content=msg,
            view=None,
        )

class UserSelectView(ui.View):
    def __init__(self, session_id: int, options: list[SelectOption]):
        super().__init__(timeout=60)
        self.add_item(UserSelect(session_id, options))

async def handle_add_session_winners(interaction: Interaction, session_id: int):
    await interaction.response.defer(ephemeral=True)

    try:
        all_users = get_all_registered_users()
        session_users = get_users_in_session(session_id)
        already_linked = [u["user_id"] for u in get_winners_in_session(session_id)]
    except Exception as e:
        await interaction.followup.send("❌ Failed to retrieve users.", ephemeral=True)
        return

    session_user_ids = {user["user_id"] for user in session_users}
    eligible_users = [u for u in all_users if u["id"] not in already_linked]
    eligible_users = [user for user in all_users if user["id"] in session_user_ids]

    if not eligible_users:
        await interaction.followup.send("✅ Everyone is already a winner.", ephemeral=True)
        return

    options = [
        SelectOption(
            label=u["nickname"] if u["nickname"] else u["username"],
            value=str(u["id"]),
        ) for u in eligible_users[:25]  # Discord limit
    ]

    if not options:
        await interaction.followup.send("❌ No eligible users to display.", ephemeral=True)
        return

    view = UserSelectView(session_id, options)
    await interaction.followup.send("👥 Select users to add to the session:", view=view, ephemeral=True)
