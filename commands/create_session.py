import discord
from discord import Interaction, ui, SelectOption, app_commands
from helpers.supa_helpers import search_games_fuzzy, create_session_entry, get_all_registered_users, link_user_to_session

class GameSelect(ui.Select):
    def __init__(self, games, session_name, session_date):
        self.session_name = session_name
        self.session_date = session_date
        options = [SelectOption(label=game["name"], value=str(game["id"])) for game in games]
        super().__init__(placeholder="Select the game for this session", options=options)

    async def callback(self, interaction: Interaction):
        game_id = int(self.values[0])
        session = create_session_entry(game_id, name=self.session_name, date=self.session_date)

        if session:
            # Prompt to add users after confirming session creation
            view = build_user_select_view(session["id"])
            await interaction.response.edit_message(
                content=f"✅ Session for **{self.session_name or session['name_id']}** on **{self.session_date}** created!\n\n👥 Now select players for the session:",
                view=view
            )
        else:
            await interaction.response.edit_message(content="❌ Failed to create session.", view=None)


class GameSelectView(ui.View):
    def __init__(self, games, session_name, session_date):
        super().__init__(timeout=60)
        self.add_item(GameSelect(games, session_name, session_date))

async def handle_create_session(interaction: Interaction, query: str, session_name: str = None, session_date: str = None):
    await interaction.response.defer(ephemeral=True)

    games = search_games_fuzzy(query)
    if not games:
        await interaction.followup.send("❌ No games matched your search. Try `/add_game` first.", ephemeral=True)
        return

    view = GameSelectView(games, session_name, session_date)
    await interaction.followup.send("🎯 Select the game you played:", view=view, ephemeral=True)

def build_user_select_view(session_id: int):
    users = get_all_registered_users()
    options = [
        SelectOption(
            label=u["nickname"] if u["nickname"] else u["username"],
            value=str(u["id"])
        )
        for u in users[:25]  # Discord max is 25 options
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
            for user_id in selected_ids:
                link_user_to_session(session_id, user_id)
            await interaction.response.edit_message(
                content="✅ Users added to the session!", view=None
            )

    class UserSelectView(ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.add_item(UserSelect())

    return UserSelectView()
