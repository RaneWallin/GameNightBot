import aiohttp
import xml.etree.ElementTree as ET
from discord import Interaction, ui, ButtonStyle
from helpers.supa_helpers import (
    get_or_create_user,
    get_or_create_game,
    user_has_game,
    link_user_game,
)

async def handle_add_game(interaction: Interaction, query: str):
    await interaction.response.defer(ephemeral=True)

    search_url = f"https://boardgamegeek.com/xmlapi2/search?query={query}&type=boardgame"
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as response:
            xml = await response.text()
            root = ET.fromstring(xml)
            items = root.findall("item")

            if not items:
                await interaction.followup.send("❌ No matching games found.", ephemeral=True)
                return

            top_games = items[:20]
            game_options = []

            for item in top_games:
                bgg_id = int(item.get("id"))
                name = item.find("name").get("value")
                year_tag = item.find("yearpublished")
                year = year_tag.get("value") if year_tag is not None else "N/A"
                game_options.append((bgg_id, name, f"{name} ({year})"))

            class GameButton(ui.Button):
                def __init__(self, index, label):
                    super().__init__(label=label, style=ButtonStyle.primary)
                    self.index = index

                async def callback(self, button_interaction: Interaction):
                    if button_interaction.user.id != interaction.user.id:
                        await button_interaction.response.send_message("❌ You can't select for another user.", ephemeral=True)
                        return

                    bgg_id, name, _ = game_options[self.index]
                    await button_interaction.response.edit_message(content=f"✅ You selected **{name}**", view=None)
                    await process_selected_game(interaction, bgg_id)

            class GameButtonView(ui.View):
                def __init__(self):
                    super().__init__(timeout=60)
                    for idx, (_, _, label) in enumerate(game_options):
                        self.add_item(GameButton(idx, label))

            view = GameButtonView()
            await interaction.followup.send("🔍 Select the game you want to add:", view=view, ephemeral=True)

async def process_selected_game(interaction: Interaction, bgg_id: int):
    async with aiohttp.ClientSession() as session:
        thing_url = f"https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}&stats=1"
        async with session.get(thing_url) as response:
            game_xml = await response.text()
            root = ET.fromstring(game_xml)
            game = root.find("item")
            name = game.find("name").get("value")
            min_players = int(game.find("minplayers").get("value"))
            max_players = int(game.find("maxplayers").get("value"))
            publisher = next((e.get("value") for e in game.findall("link") if e.get("type") == "boardgamepublisher"), "")
            designer = next((e.get("value") for e in game.findall("link") if e.get("type") == "boardgamedesigner"), "")

    user_id = get_or_create_user(interaction.user)
    game_id = get_or_create_game(bgg_id, {
        "name": name,
        "publisher": publisher,
        "designer": designer,
        "min_players": min_players,
        "max_players": max_players
    })

    if user_has_game(user_id, game_id):
        await interaction.followup.send(f"✅ **{name}** is already in your collection.", ephemeral=True)
    else:
        link_user_game(user_id, game_id)
        await interaction.followup.send(f"🎉 Added **{name}** to your collection!", ephemeral=True)
