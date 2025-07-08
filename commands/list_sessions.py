import discord
from discord import Interaction, ui, ButtonStyle
from helpers.supa_helpers import (
    search_games_fuzzy,
    get_sessions_for_game,
    get_winners_in_session,
    get_users_by_ids
)
from helpers.input_sanitizer import sanitize_query_input
from math import ceil


class GameSessionPaginator(ui.View):
    def __init__(self, game_name: str, sessions: list[dict], per_page: int = 5):
        super().__init__(timeout=60)
        self.game_name = game_name
        self.sessions = sessions
        self.per_page = per_page
        self.page = 0
        self.total_pages = ceil(len(sessions) / per_page)

        self.prev_button = ui.Button(label="⬅️ Prev", style=ButtonStyle.secondary)
        self.next_button = ui.Button(label="Next ➡️", style=ButtonStyle.secondary)

        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.update_buttons()
        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    def update_buttons(self):
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page >= self.total_pages - 1

    def get_page_content(self):
        start = self.page * self.per_page
        end = start + self.per_page
        sessions_page = self.sessions[start:end]
        lines = []

        for s in sessions_page:
            winners_ids = get_winners_in_session(s["id"])
            if winners_ids:
                winner_users = get_users_by_ids(winners_ids)
                winner_names = [u.get("nickname") or u.get("username") for u in winner_users]
                winner_text = ", ".join(winner_names)
            else:
                winner_text = "not selected"

            lines.append(
                f"**Session ID: {s.get('id', '?')} - {s.get('date', 'No Date')}** — {s.get('name') or '(no name)'}\n"
                f"   🏆 Winners: {winner_text}"
            )

        return f"📋 Sessions for **{self.game_name}** (Page {self.page + 1}/{self.total_pages}):\n\n" + "\n\n".join(lines)

    async def prev_page(self, interaction: Interaction):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(content=self.get_page_content(), view=self)

    async def next_page(self, interaction: Interaction):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(content=self.get_page_content(), view=self)


async def handle_list_sessions(interaction: Interaction, query: str):
    await interaction.response.defer(ephemeral=True)
    query = sanitize_query_input(query)

    try:
        games = search_games_fuzzy(query)
    except Exception as e:
        await interaction.followup.send(f"❌ Error searching for games: {str(e)}", ephemeral=True)
        return

    if not games:
        await interaction.followup.send("❌ No matching games found. Try using `/add_game` first.", ephemeral=True)
        return

    class GameButton(ui.Button):
        def __init__(self, game_id: int, label: str):
            super().__init__(label=label[:80], style=ButtonStyle.primary)
            self.game_id = game_id
            self.label_text = label

        async def callback(self, i: Interaction):
            try:
                sessions = get_sessions_for_game(self.game_id, i.guild_id)
            except Exception as e:
                await i.response.edit_message(content=f"❌ Failed to fetch sessions: {str(e)}", view=None)
                return

            if not sessions:
                await i.response.edit_message(content="📭 No sessions found for that game.", view=None)
                return

            view = GameSessionPaginator(self.label_text, sessions)
            await i.response.edit_message(content=view.get_page_content(), view=view)

    class GameButtonView(ui.View):
        def __init__(self, games):
            super().__init__(timeout=60)
            for game in games[:20]:  # Discord allows max 25 buttons per view
                self.add_item(GameButton(game["id"], game["name"]))

    view = GameButtonView(games)
    await interaction.followup.send("🎲 Select the game to view sessions:", view=view, ephemeral=True)
