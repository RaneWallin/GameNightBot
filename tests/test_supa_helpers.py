import pytest
from unittest.mock import patch, MagicMock
from helpers import supa_helpers

@patch("helpers.supa_helpers.supabase")
def test_get_or_create_user_existing(mock_supabase):
    # Simulate user already exists
    mock_supabase.table().select().eq().execute.return_value.data = [{"id": 42}]
    user_id = supa_helpers.get_or_create_user(MagicMock(id=123, __str__=lambda s: "test#1234"))
    assert user_id == 42

@patch("helpers.supa_helpers.supabase")
def test_get_or_create_user_new(mock_supabase):
    # Simulate user does not exist
    mock_supabase.table().select().eq().execute.return_value.data = []
    mock_supabase.table().insert().execute.return_value.data = [{"id": 99}]
    user_id = supa_helpers.get_or_create_user(MagicMock(id=123, __str__=lambda s: "test#1234"))
    assert user_id == 99
