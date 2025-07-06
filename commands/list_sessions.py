import discord
from discord import Interaction, ui, ButtonStyle
from helpers.supa_helpers import search_games_fuzzy, get_sessions_for_game
from helpers.input_sanitizer import sanitize_query_input


async def handle_list_sessions(interaction: Interaction, query: str):
    await interaction.response.defer(ephemeral=True)
    query = sanitize_query_input(query)

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

    class GameButton(ui.Button):
        def __init__(self, game_id: int, label: str):
            super().__init__(label=label[:80], style=ButtonStyle.primary)
            self.game_id = game_id

        async def callback(self, i: Interaction):
            try:
                sessions = get_sessions_for_game(self.game_id, i.guild_id)
            except Exception as e:
                await i.response.edit_message(
                    content=f"❌ Failed to fetch sessions: {str(e)}", view=None
                )
                return

            if not sessions:
                await i.response.edit_message(
                    content="📭 No sessions found for that game.", view=None
                )
                return

            session_lines = [
                f"🗓️ **Session ID: {s.get('id', '?')} - {s.get('date', 'No Date')}** — {s.get('name') or '(no name)'}"
                for s in sessions
            ]
            session_text = "\n".join(session_lines)

            await i.response.edit_message(
                content=f"📋 Sessions for selected game:\n\n{session_text}",
                view=None
            )

    class GameButtonView(ui.View):
        def __init__(self, games):
            super().__init__(timeout=60)
            for game in games[:20]:  # Discord allows max 25 buttons in one view
                self.add_item(GameButton(game["id"], game["name"]))

    view = GameButtonView(games)
    await interaction.followup.send(
        "🎲 Select the game to view sessions:", view=view, ephemeral=True
    )
