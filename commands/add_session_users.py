import discord
from discord import Interaction, ui, SelectOption
from helpers.supa_helpers import get_all_registered_users, get_users_in_session, link_user_to_session

class UserSelect(ui.Select):
    def __init__(self, session_id: int, options: list[SelectOption]):
        self.session_id = session_id
        super().__init__(
            placeholder="Select users to add to this session",
            min_values=1,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: Interaction):
        selected_ids = [int(uid) for uid in self.values]
        for user_id in selected_ids:
            link_user_to_session(self.session_id, user_id)
        await interaction.response.edit_message(
            content="✅ Users successfully added to the session!",
            view=None
        )

class UserSelectView(ui.View):
    def __init__(self, session_id: int, options: list[SelectOption]):
        super().__init__(timeout=60)
        self.add_item(UserSelect(session_id, options))

async def handle_add_session_users(interaction: Interaction, session_id: int):
    await interaction.response.defer(ephemeral=True)

    all_users = get_all_registered_users()
    already_linked = [u["user_id"] for u in get_users_in_session(session_id)]

    # Filter out already linked users
    eligible_users = [u for u in all_users if u["id"] not in already_linked]

    if not eligible_users:
        await interaction.followup.send("✅ Everyone is already in this session.", ephemeral=True)
        return

    options = [
        SelectOption(
            label=u["nickname"] if u["nickname"] else u["username"],
            value=str(u["id"])
        ) for u in eligible_users[:25]  # Discord max is 25
    ]

    view = UserSelectView(session_id, options)
    await interaction.followup.send("👥 Select users to add to the session:", view=view, ephemeral=True)
