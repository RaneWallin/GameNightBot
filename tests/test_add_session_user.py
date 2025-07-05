import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from discord import Interaction, ui
from commands.add_session_users import handle_add_session_users, UserSelect, UserSelectView

# Sample user data
MOCK_USERS = [
    {"id": 1, "username": "user1", "nickname": "User One"},
    {"id": 2, "username": "user2", "nickname": "User Two"},
    {"id": 3, "username": "user3", "nickname": ""},
    {"id": 4, "username": "user4", "nickname": "User Four"},
]

# Test case when no users are eligible to add
@pytest.mark.asyncio
@patch("commands.add_session_users.get_all_registered_users", return_value=MOCK_USERS)
@patch("commands.add_session_users.get_users_in_session", return_value=[{"user_id": 1}, {"user_id": 2}, {"user_id": 3}, {"user_id": 4}])
@patch("commands.add_session_users.link_user_to_session")
async def test_handle_add_session_users_no_eligible_users(mock_link_user_to_session, mock_get_users_in_session, mock_get_all_registered_users):
    # Mock interaction
    interaction = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    session_id = 123  # Example session ID

    # Run the function
    await handle_add_session_users(interaction, session_id)

    # Ensure no users were added
    mock_link_user_to_session.assert_not_called()

    # Check that the response was sent saying everyone is already in the session
    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once_with("✅ Everyone is already in this session.", ephemeral=True)

# Test case when there is a failure during user retrieval or linking
@pytest.mark.asyncio
@patch("commands.add_session_users.get_all_registered_users", side_effect=Exception("Database error"))
@patch("commands.add_session_users.get_users_in_session")
@patch("commands.add_session_users.link_user_to_session")
async def test_handle_add_session_users_failure(mock_link_user_to_session, mock_get_users_in_session, mock_get_all_registered_users):
    # Mock interaction
    interaction = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    session_id = 123  # Example session ID

    # Run the function
    await handle_add_session_users(interaction, session_id)

    # Ensure no functions for linking were called
    mock_link_user_to_session.assert_not_called()

    # Check that the error message was sent
    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once_with("❌ Failed to retrieve users.", ephemeral=True)
