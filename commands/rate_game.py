import discord
from discord import Interaction, ui
from datetime import datetime, timedelta
from helpers.supa_helpers import search_games_fuzzy, add_or_update_rating, get_user_by_discord_id

POLL_DURATION_DAYS = 7

class RatingButton(ui.Button):
    def __init__(self, game_id: int, label: str, rating: int):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.game_id = game_id
        self.rating = rating

    async def callback(self, interaction: Interaction):
        user = interaction.user
        expires_at = datetime.utcnow() + timedelta(days=POLL_DURATION_DAYS)
        user_record = get_user_by_discord_id(user.id, interaction.guild_id)
        if not user_record:
            await interaction.response.send_message("❌ You must register first using `/register_user`.", ephemeral=True)
            return

        user_id = user_record["id"]  # Supabase user ID
        
        add_or_update_rating(user_id, self.game_id, self.rating, expires_at)

        await interaction.response.send_message(
            f"⭐ You rated the game **{self.rating}/5**. Thanks!",
            ephemeral=True
        )

class RatingView(ui.View):
    def __init__(self, game_id: int):
        super().__init__(timeout=POLL_DURATION_DAYS * 86400)
        for i in range(1, 6):
            self.add_item(RatingButton(game_id, f"{i} ⭐", i))

async def handle_rate_game(interaction: Interaction, query: str):
    await interaction.response.defer(ephemeral=False)

    games = search_games_fuzzy(query)
    if not games:
        await interaction.followup.send("❌ No matching games found.")
        return

    game = games[0]
    view = RatingView(game["id"])
    await interaction.followup.send(
        f"📊 **Rate {game['name']}**\nSelect a rating from 1 to 5:",
        view=view
    )
