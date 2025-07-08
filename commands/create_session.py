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


# Step 1: Modal for name and date
from datetime import datetime

from datetime import datetime

class SessionInfoModal(discord.ui.Modal, title="Session Info"):
    name = discord.ui.TextInput(label="Session Name", required=False)
    date = discord.ui.TextInput(label="Date (YYYY-MM-DD)", required=False)

    def __init__(self, query: str, server_id: int):
        super().__init__()
        self.query = query
        self.server_id = server_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            date_str = self.date.value.strip()

            if date_str:
                try:
                    parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted_date = parsed_date.isoformat()
                except ValueError:
                    await interaction.response.send_message(
                        "❌ Invalid date format. Please use `YYYY-MM-DD` (e.g., `2025-07-06`).",
                        ephemeral=True
                    )
                    return
            else:
                formatted_date = None

            await handle_game_selection(
                interaction,
                self.query,
                self.server_id,
                self.name.value.strip(),
                formatted_date
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred while processing your input: `{str(e)}`",
                ephemeral=True
            )

# Step 2: Dropdown to select the game
class GameSelect(ui.Select):
    def __init__(self, games, session_name: str | None, session_date: str | None, server_id: int):
        self.session_name = session_name
        self.session_date = session_date
        self.server_id = server_id
        options = [SelectOption(label=game["name"], value=str(game["id"])) for game in games]
        super().__init__(placeholder="Select the game for this session", options=options)

    async def callback(self, interaction: Interaction):
        game_id = int(self.values[0])
        session = create_session_entry(game_id, self.server_id, name=self.session_name, date=self.session_date)

        if session:
            view = build_user_select_view(session["id"], self.server_id)
            await interaction.response.edit_message(
                content=f"✅ Session for **{self.session_name or 'Unnamed'}** on **{self.session_date or 'unspecified'}** created!\n\n👥 Now select players for the session:",
                view=view
            )
        else:
            await interaction.response.edit_message(content="❌ Failed to create session.", view=None)


class GameSelectView(ui.View):
    def __init__(self, games, session_name, session_date, server_id):
        super().__init__(timeout=60)
        self.add_item(GameSelect(games, session_name, session_date, server_id))


# Handles game selection after modal
async def handle_game_selection(interaction: Interaction, query: str, server_id: int, session_name: str, session_date: str):
    query = sanitize_query_input(query)
    games = search_games_fuzzy(query)

    if not games:
        await interaction.followup.send("❌ No games matched your search.", ephemeral=True)
        return

    view = GameSelectView(games, session_name, session_date, server_id)
    await interaction.response.send_message("🎯 Select the game you played:", view=view, ephemeral=True)



# Slash command entry point
async def handle_create_session(interaction: Interaction, game_query: str):
    await interaction.response.send_modal(SessionInfoModal(game_query, interaction.guild_id))


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
                content=f"✅ Added {added} user(s) to the session!",
                view=None
            )

    class UserSelectView(ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            if options:
                self.add_item(UserSelect())

    return UserSelectView()
