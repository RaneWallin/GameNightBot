import discord
from discord import Interaction, ui, ButtonStyle
from helpers.supa_helpers import get_user_id_by_discord, get_user_games_sorted_by_name

class GamePagination(ui.View):
    def __init__(self, pages):
        super().__init__(timeout=60)
        self.pages = pages
        self.current = 0

    @ui.button(label="Prev", style=ButtonStyle.secondary)
    async def prev(self, interaction: Interaction, button: ui.Button):
        if self.current > 0:
            self.current -= 1
            await interaction.response.edit_message(content=self.pages[self.current], view=self)

    @ui.button(label="Next", style=ButtonStyle.secondary)
    async def next(self, interaction: Interaction, button: ui.Button):
        if self.current < len(self.pages) - 1:
            self.current += 1
            await interaction.response.edit_message(content=self.pages[self.current], view=self)

async def handle_my_games(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    discord_id = int(interaction.user.id)

    user_id = get_user_id_by_discord(discord_id)
    if not user_id:
        await interaction.followup.send("❌ You haven't added any games yet.", ephemeral=True)
        return

    game_names = get_user_games_sorted_by_name(user_id)
    if not game_names:
        await interaction.followup.send("🕹️ You don't have any games in your collection.", ephemeral=True)
        return

    page_size = 10
    pages = ["\n".join(f"\u2022 {name}" for name in game_names[i:i + page_size]) for i in range(0, len(game_names), page_size)]
    pages = [f"\ud83d\udcda **Your Games (Page {i + 1}/{len(pages)}):**\n{page}" for i, page in enumerate(pages)]

    view = GamePagination(pages)
    await interaction.followup.send(content=pages[0], view=view, ephemeral=True)