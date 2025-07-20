import discord
from discord import Interaction, ui, SelectOption
from helpers.supa_helpers import (
    search_games_fuzzy,
    create_session_entry,
    get_all_registered_users,
    get_users_in_session,
    link_user_to_session
)
from helpers.input_sanitizer import sanitize_query_input
from datetime import datetime

# Step 1: Modal for name and date
class SessionInfoModal(discord.ui.Modal, title="Session Info"):
    name = discord.ui.TextInput(label="Session Name", required=False)
    date = discord.ui.TextInput(label="Date (YYYY-MM-DD)", required=False)

    def __init__(self, game_id: int, server_id: int):
        super().__init__()
        self.game_id = game_id
        self.server_id = server_id

    async def on_submit(self, interaction: Interaction):
        try:
            date_str = self.date.value.strip()
            if date_str:
                try:
                    parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted_date = parsed_date.isoformat()
                except ValueError:
                    await interaction.response.send_message(
                        "❌ Invalid date format. Please use `YYYY-MM-DD`.",
                        ephemeral=True
                    )
                    return
            else:
                formatted_date = None

            session = create_session_entry(
                self.game_id,
                self.server_id,
                name=self.name.value.strip(),
                date=formatted_date
            )

            if session:
                view = build_user_select_view(session["id"], self.server_id)
                await interaction.response.send_message(
                    f"✅ Session {session.get('id', '(Error gettings id)')} **{session.get('name', '(unnamed)')}** created for **{session.get('date', 'unspecified')}**!\nNow select players:",
                    view=view,
                    ephemeral=True
                )
            else:
                await interaction.response.send_message("❌ Failed to create session.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error: `{str(e)}`", ephemeral=True)


# Step 2: Dropdown to select a game
class GameSelect(ui.Select):
    def __init__(self, games, server_id: int):
        self.server_id = server_id
        options = [SelectOption(label=game["name"], value=str(game["id"])) for game in games]
        super().__init__(placeholder="Select the game you played", options=options)

    async def callback(self, interaction: Interaction):
        game_id = int(self.values[0])
        await interaction.response.send_modal(SessionInfoModal(game_id, self.server_id))


class GameSelectView(ui.View):
    def __init__(self, games, server_id: int):
        super().__init__(timeout=60)
        self.add_item(GameSelect(games, server_id))


# Entry point from slash command
async def handle_create_session(interaction: Interaction, game_query: str):
    await interaction.response.defer(ephemeral=True)
    query = sanitize_query_input(game_query)
    games = search_games_fuzzy(query)

    if not games:
        await interaction.followup.send("❌ No games matched your search.", ephemeral=True)
        return

    view = GameSelectView(games, interaction.guild_id)
    await interaction.followup.send("🎯 Select the game you played:", view=view, ephemeral=True)


# User picker view
def build_user_select_view(session_id: int, server_id: int):
    users = get_all_registered_users(server_id)
    already_linked = {u["user_id"] for u in get_users_in_session(session_id)}
    eligible_users = [u for u in users if u["id"] not in already_linked]

    options = [
        SelectOption(
            label=u["nickname"] if u["nickname"] else u["username"],
            value=str(u["id"])
        )
        for u in eligible_users[:25]
    ]

    class UserSelect(ui.Select):
        def __init__(self):
            super().__init__(
                placeholder="Select players for this session",
                min_values=1,
                max_values=len(options),
                options=options
            )

        async def callback(self, interaction: Interaction):
            selected_ids = [int(uid) for uid in self.values]
            added = 0
            for user_id in selected_ids:
                try:
                    link_user_to_session(session_id, user_id)
                    added += 1
                except Exception:
                    pass

            await interaction.response.edit_message(
                content=f"✅ Added {added} user(s) to session {session_id}!",
                view=None
            )

    class UserSelectView(ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            if options:
                self.add_item(UserSelect())

    return UserSelectView()
