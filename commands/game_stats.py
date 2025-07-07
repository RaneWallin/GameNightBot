import discord
from discord import Interaction, ui, ButtonStyle
from helpers.supa_helpers import (
    search_games_fuzzy,
    get_sessions_for_game,
    get_winners_in_session,
    get_users_by_ids
)
from collections import Counter


class ShareStatsButton(ui.View):
    def __init__(self, message_content: str):
        super().__init__(timeout=60)
        self.message_content = message_content
        self.add_item(self.ShareButton(message_content))

    class ShareButton(ui.Button):
        def __init__(self, message_content: str):
            super().__init__(label="📢 Share Publicly", style=ButtonStyle.primary)
            self.message_content = message_content

        async def callback(self, interaction: Interaction):
            self.disabled = True
            await interaction.channel.send(self.message_content)


class GameSelectView(ui.View):
    def __init__(self, games: list[dict], interaction: Interaction):
        super().__init__(timeout=60)
        for game in games[:5]:  # Discord recommends max 5 buttons per row
            self.add_item(self.GameButton(game, interaction))

    class GameButton(ui.Button):
        def __init__(self, game: dict, interaction: Interaction):
            super().__init__(label=game["name"], style=ButtonStyle.secondary)
            self.game = game
            self.interaction = interaction

        async def callback(self, interaction: Interaction):
            sessions = get_sessions_for_game(self.game["id"], interaction.guild_id)
            if not sessions:
                await interaction.response.edit_message(
                    content=f"📉 **{self.game['name']}** has no logged sessions yet.",
                    view=None
                )
                return

            total_plays = len(sessions)
            win_counter = Counter()

            for session in sessions:
                winners = get_winners_in_session(session["id"])
                win_counter.update(winners)

            top_winners = win_counter.most_common(3)
            if not top_winners:
                winners_text = "_No winners have been recorded yet._"
            else:
                user_ids = [uid for uid, _ in top_winners]
                users = get_users_by_ids(user_ids)
                id_to_name = {u["id"]: u.get("nickname") or u.get("username") for u in users}
                winners_text = "\n".join(
                    f"🏆 {id_to_name.get(uid, 'Unknown')} — {count} win(s)"
                    for uid, count in top_winners
                )

            content = (
                f"📊 **Stats for {self.game['name']}**\n"
                f"• 🎮 Total plays: **{total_plays}**\n"
                f"{winners_text}"
            )

            await interaction.response.edit_message(
                content=content,
                view=ShareStatsButton(content)
            )


async def handle_game_stats(interaction: Interaction, query: str):
    await interaction.response.defer(ephemeral=True)

    matched_games = search_games_fuzzy(query)
    if not matched_games:
        await interaction.followup.send("❌ No games matched your query.", ephemeral=True)
        return

    if len(matched_games) == 1:
        # Shortcut: only one result, auto-select
        game = matched_games[0]
        button = GameSelectView.GameButton(game, interaction)
        await button.callback(interaction)
    else:
        await interaction.followup.send(
            "🎯 Multiple games matched. Select one to view stats:",
            view=GameSelectView(matched_games, interaction),
            ephemeral=True
        )
