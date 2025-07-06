import aiohttp
import xml.etree.ElementTree as ET
from discord import Interaction, ui, ButtonStyle
from helpers.supa_helpers import (
    get_user_by_discord_id,
    get_or_create_game,
    user_has_game,
    link_user_game,
)
from helpers.input_sanitizer import sanitize_query_input, escape_query_param


async def handle_add_game(interaction: Interaction, query: str):
    user = get_user_by_discord_id(interaction.user.id)

    if not user:
        await interaction.followup.send("❌ User is not registered. Try using /register_user.", ephemeral=True)
        return 

    await interaction.response.defer(ephemeral=True)
    query = sanitize_query_input(query)
    query = escape_query_param(query)

    search_url = f"https://boardgamegeek.com/xmlapi2/search?query={query}&type=boardgame"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(search_url) as response:
                if response.status != 200:
                    await interaction.followup.send("❌ Failed to fetch data from BoardGameGeek.", ephemeral=True)
                    return
                xml = await response.text()
    except Exception as e:
        await interaction.followup.send("❌ Network error while contacting BGG.", ephemeral=True)
        return

    try:
        root = ET.fromstring(xml)
        items = root.findall("item")
    except ET.ParseError:
        await interaction.followup.send("❌ Could not parse BGG's response.", ephemeral=True)
        return

    if not items:
        await interaction.followup.send("❌ No matching games found.", ephemeral=True)
        return

    top_games = items[:20]  # Limit to 20 to prevent UI overload
    game_options = []

    for item in top_games:
        bgg_id = int(item.get("id"))
        name_tag = item.find("name")
        name = name_tag.get("value") if name_tag is not None else "Unknown Game"
        year_tag = item.find("yearpublished")
        year = year_tag.get("value") if year_tag is not None else "N/A"

        max_name_length = 80 - len(f" ({year})")
        trimmed_name = name[:max_name_length - 1] + "…" if len(name) > max_name_length else name
        label = f"{trimmed_name} ({year})"

        game_options.append((bgg_id, name, label))

    class GameButton(ui.Button):
        def __init__(self, index: int, label: str):
            super().__init__(label=label, style=ButtonStyle.primary)
            self.index = index

        async def callback(self, button_interaction: Interaction):
            if button_interaction.user.id != interaction.user.id:
                await button_interaction.response.send_message("❌ You can't select for another user.", ephemeral=True)
                return

            bgg_id, name, _ = game_options[self.index]
            await button_interaction.response.edit_message(content=f"✅ You selected **{name}**", view=None)
            await process_selected_game(interaction, bgg_id, user["id"])

    class GameButtonView(ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            for idx, (_, _, label) in enumerate(game_options):
                self.add_item(GameButton(idx, label))

    view = GameButtonView()
    await interaction.followup.send("🔍 Select the game you want to add:", view=view, ephemeral=True)

async def process_selected_game(interaction: Interaction, bgg_id: int, user_id: int):
    thing_url = f"https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}&stats=1"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(thing_url) as response:
                if response.status != 200:
                    await interaction.followup.send("❌ Failed to fetch game details from BGG.", ephemeral=True)
                    return
                game_xml = await response.text()
                root = ET.fromstring(game_xml)
                game = root.find("item")
    except Exception:
        await interaction.followup.send("❌ Could not retrieve game details.", ephemeral=True)
        return

    if game is None:
        await interaction.followup.send("❌ Game details not found.", ephemeral=True)
        return

    name = game.find("name").get("value", "Unknown Game")
    min_players = int(game.find("minplayers").get("value", 0))
    max_players = int(game.find("maxplayers").get("value", 0))
    publisher = next((e.get("value") for e in game.findall("link") if e.get("type") == "boardgamepublisher"), "")
    designer = next((e.get("value") for e in game.findall("link") if e.get("type") == "boardgamedesigner"), "")

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
