import aiohttp
import xml.etree.ElementTree as ET
from discord import Interaction, ui, SelectOption, Embed, ButtonStyle
from helpers.supa_helpers import get_or_create_game, get_or_create_user, user_has_game, link_user_game

async def fetch_bgg_search(query: str):
    url = f"https://boardgamegeek.com/xmlapi2/search?query={query}&type=boardgame"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            xml = await response.text()
    root = ET.fromstring(xml)
    return root.findall("item")

async def fetch_bgg_game_details(bgg_id: int):
    url = f"https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}&stats=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            xml = await response.text()
    root = ET.fromstring(xml)
    return root.find("item")

def parse_game_embed(game_xml) -> Embed:
    name = game_xml.find("name").attrib["value"]
    year = game_xml.find("yearpublished").attrib["value"]
    min_players = game_xml.find("minplayers").attrib["value"]
    max_players = game_xml.find("maxplayers").attrib["value"]
    play_time = game_xml.find("playingtime").attrib["value"]
    image_url = game_xml.find("image").text if game_xml.find("image") is not None else None

    embed = Embed(
        title=f"{name} ({year})",
        url=f"https://boardgamegeek.com/boardgame/{game_xml.attrib['id']}",
        description="BoardGameGeek Information"
    )
    embed.add_field(name="Players", value=f"{min_players} - {max_players}", inline=True)
    embed.add_field(name="Play Time", value=f"{play_time} minutes", inline=True)

    publishers = [e.attrib["value"] for e in game_xml.findall("link") if e.attrib["type"] == "boardgamepublisher"]
    designers = [e.attrib["value"] for e in game_xml.findall("link") if e.attrib["type"] == "boardgamedesigner"]

    if designers:
        embed.add_field(name="Designer", value=", ".join(designers), inline=False)
    if publishers:
        embed.add_field(name="Publisher", value=", ".join(publishers), inline=False)

    if image_url:
        embed.set_thumbnail(url=image_url)

    return embed

async def handle_game_info(interaction: Interaction, query: str):
    await interaction.response.defer(ephemeral=False)
    items = await fetch_bgg_search(query)

    if not items:
        await interaction.followup.send("❌ No games found on BoardGameGeek.")
        return

    options = []
    for item in items[:20]:
        name = item.find("name").attrib["value"]
        year = item.find("yearpublished").attrib["value"] if item.find("yearpublished") is not None else "N/A"
        label = f"{name} ({year})"
        options.append(SelectOption(label=label, value=item.attrib["id"]))

    class GameSelect(ui.Select):
        def __init__(self):
            super().__init__(placeholder="Select a game to view details", options=options)

        async def callback(self, i: Interaction):
            bgg_id = int(self.values[0])
            game_xml = await fetch_bgg_game_details(bgg_id)
            embed = parse_game_embed(game_xml)

            name = game_xml.find("name").attrib["value"]
            publisher = next((e.attrib["value"] for e in game_xml.findall("link") if e.attrib["type"] == "boardgamepublisher"), "")
            designer = next((e.attrib["value"] for e in game_xml.findall("link") if e.attrib["type"] == "boardgamedesigner"), "")
            min_players = int(game_xml.find("minplayers").attrib["value"])
            max_players = int(game_xml.find("maxplayers").attrib["value"])

            user_id = get_or_create_user(i.user)
            game_id = get_or_create_game(bgg_id, {
                "name": name,
                "publisher": publisher,
                "designer": designer,
                "min_players": min_players,
                "max_players": max_players
            })

            class AddButton(ui.Button):
                def __init__(self):
                    super().__init__(label="Add to My Collection", style=ButtonStyle.success)

                async def callback(self, button_interaction: Interaction):
                    user_id = get_or_create_user(button_interaction.user)

                    if user_has_game(user_id, game_id):
                        await button_interaction.response.send_message("✅ Game already in your collection.", ephemeral=True)
                    else:
                        link_user_game(user_id, game_id)
                        await button_interaction.response.send_message(f"🎉 Added **{name}** to your collection!", ephemeral=True)

            view = ui.View(timeout=3000)
            view.add_item(AddButton())

            await i.response.edit_message(content="", embed=embed, view=view)

    class GameSelectView(ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.add_item(GameSelect())

    await interaction.followup.send("🎲 Select a game to view details:", view=GameSelectView())
