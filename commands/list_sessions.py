import discord
from discord import Interaction, ui, SelectOption
from helpers.supa_helpers import search_games_fuzzy, get_sessions_for_game

class SessionGameSelect(ui.Select):
    def __init__(self, games):
        options = [
            SelectOption(label=g.get("name", "Unknown Game"), value=str(g["id"]))
            for g in games
        ]
        super().__init__(
            placeholder="Choose a game to list sessions",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: Interaction):
        game_id = int(self.values[0])
        try:
            sessions = get_sessions_for_game(game_id)
        except Exception as e:
            await interaction.response.edit_message(
                content=f"❌ Failed to fetch sessions: {str(e)}", view=None
            )
            return

        if not sessions:
            await interaction.response.edit_message(
                content="📭 No sessions found for that game.", view=None
            )
            return

        session_lines = [
            f"🗓️ **Session ID: {s.get('id', '?')} - {s.get('date', 'No Date')}** — {s.get('name') or '(no name)'}"
            for s in sessions
        ]
        session_text = "\n".join(session_lines)

        await interaction.response.edit_message(
            content=f"📋 Sessions for selected game:\n\n{session_text}", view=None
        )

class SessionSelectView(ui.View):
    def __init__(self, games):
        super().__init__(timeout=60)
        self.add_item(SessionGameSelect(games))

async def handle_list_sessions(interaction: Interaction, query: str):
    await interaction.response.defer(ephemeral=True)

    try:
        games = search_games_fuzzy(query)
    except Exception as e:
        await interaction.followup.send(
            f"❌ Error searching for games: {str(e)}", ephemeral=True
        )
        return

    if not games:
        await interaction.followup.send(
            "❌ No matching games found. Try using `/add_game` first.", ephemeral=True
        )
        return

    view = SessionSelectView(games)
    await interaction.followup.send(
        "🎲 Select the game to view sessions:", view=view, ephemeral=True
    )
