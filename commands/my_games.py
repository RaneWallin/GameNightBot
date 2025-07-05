import discord
from discord import Interaction, ui, ButtonStyle
from helpers.supa_helpers import get_user_id_by_discord, get_user_games_sorted_by_name

class GamePagination(ui.View):
    def __init__(self, pages: list[str]):
        super().__init__(timeout=120)
        self.pages = pages
        self.current = 0

    @ui.button(label="⬅️ Prev", style=ButtonStyle.secondary)
    async def prev(self, interaction: Interaction, button: ui.Button):
        if self.current > 0:
            self.current -= 1
            await interaction.response.edit_message(content=self.pages[self.current], view=self)
        else:
            await interaction.response.defer()

    @ui.button(label="Next ➡️", style=ButtonStyle.secondary)
    async def next(self, interaction: Interaction, button: ui.Button):
        if self.current < len(self.pages) - 1:
            self.current += 1
            await interaction.response.edit_message(content=self.pages[self.current], view=self)
        else:
            await interaction.response.defer()

async def handle_my_games(interaction: Interaction, user: discord.User = None):
    await interaction.response.defer(ephemeral=True)

    if user is None:
        user = interaction.user

    user_id = get_user_id_by_discord(int(user.id))
    if not user_id:
        await interaction.followup.send("❌ You aren't registered yet. Use `/register_user` to begin.", ephemeral=True)
        return

    game_names = get_user_games_sorted_by_name(user_id)
    if not game_names:
        await interaction.followup.send("🕹️ You don't have any games in your collection. Use `/add_game` to add one.", ephemeral=True)
        return

    page_size = 10
    total_pages = (len(game_names) + page_size - 1) // page_size

    pages = [
        f"📚 **Your Games (Page {i + 1}/{total_pages})**:\n" +
        "\n".join(f"• {name}" for name in game_names[i:i + page_size])
        for i in range(0, len(game_names), page_size)
    ]

    view = GamePagination(pages)
    await interaction.followup.send(content=pages[0], view=view, ephemeral=True)
