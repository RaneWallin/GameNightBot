import aiohttp
import xml.etree.ElementTree as ET
from discord import Interaction, ui, SelectOption, Embed, ButtonStyle
from helpers.supa_helpers import get_or_create_game, get_user_by_discord_id, user_has_game, link_user_game
from helpers.input_sanitizer import sanitize_query_input, escape_query_param


async def fetch_bgg_search(query: str):
    query = sanitize_query_input(query)
    query = escape_query_param(query)
    
    url = f"https://boardgamegeek.com/xmlapi2/search?query={query}&type=boardgame"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception("Failed to fetch search results from BGG.")
            xml = await response.text()
    return ET.fromstring(xml).findall("item")


async def fetch_bgg_game_details(bgg_id: int):
    url = f"https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}&stats=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception("Failed to fetch game details from BGG.")
            xml = await response.text()
    return ET.fromstring(xml).find("item")


def parse_game_embed(game_xml) -> Embed:
    try:
        name = game_xml.find("name").attrib["value"]
        year = game_xml.find("yearpublished").attrib.get("value", "N/A")
        min_players = game_xml.find("minplayers").attrib.get("value", "?")
        max_players = game_xml.find("maxplayers").attrib.get("value", "?")
        play_time = game_xml.find("playingtime").attrib.get("value", "?")
        image_url = game_xml.find("image").text if game_xml.find("image") is not None else None
    except Exception:
        return Embed(title="Error parsing game details", description="Some data may be missing or malformed.")

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

    try:
        items = await fetch_bgg_search(query)
    except Exception as e:
        await interaction.followup.send(f"❌ Error fetching game list: {str(e)}")
        return

    if not items:
        await interaction.followup.send("❌ No games found on BoardGameGeek.")
        return

    options = []
    for item in items[:20]:
        name = item.find("name").attrib.get("value", "Unknown")
        year_tag = item.find("yearpublished")
        year = year_tag.attrib.get("value", "N/A") if year_tag is not None else "N/A"
        options.append(SelectOption(label=f"{name} ({year})", value=item.attrib["id"]))

    class GameSelect(ui.Select):
        def __init__(self):
            super().__init__(placeholder="Select a game to view details", options=options)

        async def callback(self, i: Interaction):
            bgg_id = int(self.values[0])
            try:
                game_xml = await fetch_bgg_game_details(bgg_id)
                embed = parse_game_embed(game_xml)
            except Exception as e:
                await i.response.send_message(f"❌ Could not fetch game details: {str(e)}", ephemeral=True)
                return

            name = game_xml.find("name").attrib.get("value", "Unknown")
            publisher = next((e.attrib["value"] for e in game_xml.findall("link") if e.attrib["type"] == "boardgamepublisher"), "")
            designer = next((e.attrib["value"] for e in game_xml.findall("link") if e.attrib["type"] == "boardgamedesigner"), "")
            min_players = int(game_xml.find("minplayers").attrib.get("value", 0))
            max_players = int(game_xml.find("maxplayers").attrib.get("value", 0))

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
                    user = get_user_by_discord_id(button_interaction.user.id)

                    if user:
                        user_id = user.data[0]["id"]
                    else:
                        await button_interaction.response.send_message("User is not registered. Please use /register_user.")
                        return

                    if user_has_game(user_id, game_id):
                        await button_interaction.response.send_message("✅ Already in your collection.", ephemeral=True)
                    else:
                        link_user_game(user_id, game_id)
                        await button_interaction.response.send_message(f"🎉 Added **{name}** to your collection!", ephemeral=True)

            view = ui.View(timeout=300)
            view.add_item(AddButton())

            await i.response.edit_message(content="", embed=embed, view=view)

    class GameSelectView(ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.add_item(GameSelect())

    await interaction.followup.send("🎲 Select a game to view details:", view=GameSelectView())
