# remove_game.py

from discord import Interaction, ui, SelectOption
from helpers.supa_helpers import get_user_by_discord_id, get_user_games, remove_game_link

async def handle_remove_game(interaction: Interaction, query: str):
    await interaction.response.defer(ephemeral=True)
    discord_id = int(interaction.user.id)

    # Step 1: Get user info
    user = get_user_by_discord_id(discord_id)
    if not user:
        await interaction.followup.send("❌ You don't have any games to remove.", ephemeral=True)
        return
    user_id = user["id"]

    # Step 2: Get user's games
    user_games = get_user_games(user_id)
    matching_games = [g for g in user_games if query.lower() in g["name"].lower()]

    if not matching_games:
        await interaction.followup.send("❌ No matching games found in your collection.", ephemeral=True)
        return

    if len(matching_games) == 1:
        selected_game = matching_games[0]
        remove_game_link(user_id, selected_game["id"])
        await interaction.followup.send(f"🗑️ Removed **{selected_game['name']}** from your collection.", ephemeral=True)
        return

    # Step 3: Prompt user to choose one if multiple
    options = [SelectOption(label=g["name"], value=str(g["id"])) for g in matching_games[:10]]

    class RemoveDropdown(ui.Select):
        def __init__(self):
            super().__init__(placeholder="Select a game to remove", options=options)

        async def callback(self, i: Interaction):
            selected_id = int(self.values[0])
            remove_game_link(user_id, selected_id)
            await i.response.edit_message(content="🗑️ Game removed from your collection.", view=None)

    class RemoveView(ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.add_item(RemoveDropdown())

    await interaction.followup.send("Which game would you like to remove?", view=RemoveView(), ephemeral=True)
