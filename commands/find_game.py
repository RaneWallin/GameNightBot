import aiohttp
import xml.etree.ElementTree as ET
from discord import Interaction, SelectOption, ui
from helpers.supa_helpers import get_game_by_bgg_id, get_users_with_game, get_users_by_ids
from helpers.input_sanitizer import sanitize_query_input, escape_query_param


class GameDropdown(ui.Select):
    def __init__(self, options: list[SelectOption]):
        super().__init__(
            placeholder="Select a game",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: Interaction):
        selected_bgg_id = int(self.values[0])

        game = get_game_by_bgg_id(selected_bgg_id)
        if not game:
            await interaction.response.send_message("❌ Game not found in the database. Try adding it with `/add_game`.", ephemeral=True)
            return

        user_ids = get_users_with_game(game["id"])
        if not user_ids:
            await interaction.response.send_message(f"🔍 No users have **{game['name']}** in their collection.", ephemeral=True)
            return

        user_profiles = get_users_by_ids(user_ids)
        user_list = [f"• {u.get('nickname') or u.get('username', 'Unknown')}" for u in user_profiles]

        await interaction.response.send_message(
            f"👥 **{game['name']}** is owned by:\n" + "\n".join(user_list),
            ephemeral=True
        )


class GameDropdownView(ui.View):
    def __init__(self, options: list[SelectOption]):
        super().__init__(timeout=60)
        self.add_item(GameDropdown(options))


async def handle_find_game(interaction: Interaction, query: str):
    await interaction.response.defer(ephemeral=True)
    query = sanitize_query_input(query)
    query = escape_query_param(query)

    search_url = f"https://boardgamegeek.com/xmlapi2/search?query={query}&type=boardgame"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                if response.status != 200:
                    await interaction.followup.send("⚠️ Failed to contact BoardGameGeek. Try again later.", ephemeral=True)
                    return

                xml = await response.text()
    except Exception as e:
        await interaction.followup.send(f"❌ Error fetching game data: {str(e)}", ephemeral=True)
        return

    try:
        root = ET.fromstring(xml)
        items = root.findall("item")
    except ET.ParseError:
        await interaction.followup.send("❌ Error parsing BGG response.", ephemeral=True)
        return

    if not items:
        await interaction.followup.send("❌ No matching games found.", ephemeral=True)
        return

    options = []
    for item in items[:10]:
        bgg_id = item.get("id")
        name_tag = item.find("name")
        year_tag = item.find("yearpublished")

        name = name_tag.get("value") if name_tag is not None else "Unknown"
        year = year_tag.get("value") if year_tag is not None else "N/A"
        label = f"{name} ({year})"

        options.append(SelectOption(label=label, value=bgg_id))

    view = GameDropdownView(options)
    await interaction.followup.send("🔍 Select the correct game:", view=view, ephemeral=True)
