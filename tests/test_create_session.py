import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from discord import ui
from commands.create_session import handle_create_session, build_user_select_view, GameSelectView


# Sample fake game search response
MOCK_GAMES = [
    {"id": 1, "name": "Catan"},
    {"id": 2, "name": "Monopoly"},
]

# Sample mock user data
MOCK_USERS = [
    {"id": 1, "username": "user1", "nickname": "User One"},
    {"id": 2, "username": "user2", "nickname": "User Two"},
    {"id": 3, "username": "user3", "nickname": "User Three"},
    {"id": 4, "username": "user4", "nickname": "User Four"},
]


# Test handle_create_session function when there are matching games
@pytest.mark.asyncio
@patch("commands.create_session.search_games_fuzzy", return_value=MOCK_GAMES)
@patch("commands.create_session.sanitize_query_input", return_value="Catan")
async def test_handle_create_session(mock_sanitize, mock_search_games):
    # Mock interaction
    interaction = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    # Run the function
    await handle_create_session(interaction, "Catan", "Test Session", "2023-07-01")

    # Ensure that search_games_fuzzy was called with correct arguments
    mock_search_games.assert_called_once_with("Catan")

    # Ensure that the followup.send was called once to send a message about creating a session
    interaction.followup.send.assert_called_once()

    # Get the arguments passed to followup.send
    send_args = interaction.followup.send.call_args  # Get the arguments in the call

    # Ensure that the correct message was passed
    assert send_args[0][0] == "🎯 Select the game you played:"  # The message content

    # Ensure that the view is passed as an argument in the correct place
    assert isinstance(send_args[1]["view"], GameSelectView)  # Ensure it's a GameSelectView


# Test handle_create_session when no games match the query
@pytest.mark.asyncio
@patch("commands.create_session.search_games_fuzzy", return_value=[])
async def test_handle_create_session_no_games_found(mock_search_games):
    # Mock interaction
    interaction = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    # Run the function
    await handle_create_session(interaction, "NonExistingGame", "Test Session", "2023-07-01")

    # Ensure that the followup.send was called once with the "no games" message
    interaction.followup.send.assert_called_once_with(
        "❌ No games matched your search. Try `/add_game` first.", ephemeral=True
    )


# Test build_user_select_view when there are eligible users
@pytest.mark.asyncio
@patch("commands.create_session.get_all_registered_users", return_value=MOCK_USERS)
@patch("commands.create_session.get_users_in_session", return_value=[{"user_id": 1}, {"user_id": 2}])
async def test_build_user_select_view(mock_get_users, mock_get_users_in_session):
    session_id = 123  # Example session ID
    user_select_view = build_user_select_view(session_id)

    # Ensure that get_all_registered_users was called
    mock_get_users.assert_called_once()

    # Ensure that get_users_in_session was called with the correct session ID
    mock_get_users_in_session.assert_called_once_with()

    # Ensure that the UserSelectView was created correctly
    assert len(user_select_view.children) == 1  # Only two users (user3 and user4) should be eligible