import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from commands.add_game import handle_add_game, process_selected_game


# Sample fake BGG search response (XML)
FAKE_SEARCH_XML = """
<items>
  <item id="123">
    <name value="Catan"/>
    <yearpublished value="1995"/>
  </item>
</items>
"""

# Sample fake BGG thing response (XML)
FAKE_THING_XML = """
<items>
  <item id="123">
    <name value="Catan"/>
    <minplayers value="3"/>
    <maxplayers value="4"/>
    <link type="boardgamepublisher" value="Kosmos"/>
    <link type="boardgamedesigner" value="Klaus Teuber"/>
  </item>
</items>
"""

# Test handle_add_game function
@pytest.mark.asyncio
@patch("commands.add_game.aiohttp.ClientSession.get")
@patch("commands.add_game.process_selected_game")
async def test_handle_add_game_sends_buttons(mock_process_game, mock_get):
    # Prepare mocks
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=FAKE_SEARCH_XML)
    mock_get.return_value.__aenter__.return_value = mock_response

    # Mock interaction
    interaction = MagicMock()
    interaction.user.id = 1
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    # Run
    await handle_add_game(interaction, "Catan")

    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once()
    # UI rendering is handled implicitly — you can also assert button structure if needed


# Test process_selected_game function when adding a new game
@pytest.mark.asyncio
@patch("commands.add_game.aiohttp.ClientSession.get")
@patch("commands.add_game.link_user_game")
@patch("commands.add_game.user_has_game", return_value=False)
@patch("commands.add_game.get_or_create_game", return_value=456)
@patch("commands.add_game.get_or_create_user", return_value=789)
async def test_process_selected_game_adds_new_game(
    mock_get_or_create_user, mock_get_or_create_game, mock_user_has_game, mock_link_user_game, mock_aiohttp_get
):
    # Prepare mock for game details
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value=FAKE_THING_XML)
    mock_aiohttp_get.return_value.__aenter__.return_value = mock_response

    # Mock interaction
    interaction = MagicMock()
    interaction.user.id = 1
    interaction.user.__str__.return_value = "User#1234"
    interaction.followup.send = AsyncMock()

    # Run the function
    await process_selected_game(interaction, 123)

    # Ensure that the correct functions were called
    mock_get_or_create_user.assert_called_once_with(interaction.user)
    mock_get_or_create_game.assert_called_once()
    mock_link_user_game.assert_called_once_with(789, 456)
    interaction.followup.send.assert_called_once_with("🎉 Added **Catan** to your collection!", ephemeral=True)


# Test process_selected_game function when game is already owned
@pytest.mark.asyncio
@patch("commands.add_game.aiohttp.ClientSession.get")
@patch("commands.add_game.link_user_game")
@patch("commands.add_game.user_has_game", return_value=True)  # Make sure it returns True here
@patch("commands.add_game.get_or_create_game", return_value=456)
@patch("commands.add_game.get_or_create_user", return_value=789)
async def test_process_selected_game_already_owned(
    mock_get_or_create_user, mock_get_or_create_game, mock_user_has_game, mock_link_user_game, mock_aiohttp_get
):
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value=FAKE_THING_XML)
    mock_aiohttp_get.return_value.__aenter__.return_value = mock_response

    # Mock interaction
    interaction = MagicMock()
    interaction.user.id = 1
    interaction.followup.send = AsyncMock()

    await process_selected_game(interaction, 123)

    mock_link_user_game.assert_not_called()
    interaction.followup.send.assert_called_once_with("✅ **Catan** is already in your collection.", ephemeral=True)
