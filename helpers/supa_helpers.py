from supabase import create_client, Client
from typing import Optional, Tuple
import os
from dotenv import load_dotenv
from thefuzz import fuzz

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_or_create_user(discord_user) -> int:
    discord_id = int(discord_user.id)
    username = str(discord_user)
    result = supabase.table("users").select("id").eq("discord_id", discord_id).execute()
    if result.data:
        return result.data[0]["id"]
    insert_result = supabase.table("users").insert({
        "discord_id": discord_id,
        "username": username,
        "nickname": ""
    }).execute()
    return insert_result.data[0]["id"]

def get_or_create_game(bgg_id: int, game_data: dict) -> int:
    result = supabase.table("games").select("id").eq("bgg_id", bgg_id).execute()
    if result.data:
        return result.data[0]["id"]
    insert_result = supabase.table("games").insert({
        "bgg_id": bgg_id,
        "name": game_data["name"],
        "publisher": game_data["publisher"],
        "designer": game_data["designer"],
        "min_players": game_data["min_players"],
        "max_players": game_data["max_players"]
    }).execute()
    return insert_result.data[0]["id"]

def user_has_game(user_id: int, game_id: int) -> bool:
    result = supabase.table("users_games").select("*").eq("user_id", user_id).eq("game_id", game_id).execute()
    return bool(result.data)

def link_user_game(user_id: int, game_id: int):
    supabase.table("users_games").insert({
        "user_id": user_id,
        "game_id": game_id
    }).execute()

def get_user_by_discord_id(discord_id: int) -> Optional[dict]:
    result = supabase.table("users").select("*").eq("discord_id", discord_id).execute()
    if result.data:
        return result.data[0]
    return None

def create_user(discord_id: int, username: str, nickname: str = "") -> bool:
    result = supabase.table("users").insert({
        "discord_id": discord_id,
        "username": username,
        "nickname": nickname
    }).execute()
    return bool(result.data)

def get_owned_game_ids(user_id: int) -> list:
    result = supabase.table("users_games").select("game_id").eq("user_id", user_id).execute()
    return [entry["game_id"] for entry in result.data]

def get_games_by_ids(game_ids: list) -> list:
    result = supabase.table("games").select("id, name").in_("id", game_ids).order("name").execute()
    return result.data

def remove_game_link(user_id: int, game_id: int):
    supabase.table("users_games").delete().eq("user_id", user_id).eq("game_id", game_id).execute()

def search_user_games_by_name(user_id: int, query: str) -> list:
    game_links = supabase.table("users_games").select("game_id").eq("user_id", user_id).execute()
    game_ids = [g["game_id"] for g in game_links.data]
    if not game_ids:
        return []
    games_result = supabase.table("games").select("id, name").in_("id", game_ids).execute()
    return [g for g in games_result.data if query.lower() in g["name"].lower()]

def find_game_by_bgg_id(bgg_id: int) -> Optional[dict]:
    result = supabase.table("games").select("id, name").eq("bgg_id", bgg_id).execute()
    if result.data:
        return result.data[0]
    return None

def find_users_with_game(game_id: int) -> list:
    user_links = supabase.table("users_games").select("user_id").eq("game_id", game_id).execute()
    user_ids = [u["user_id"] for u in user_links.data]
    if not user_ids:
        return []
    user_result = supabase.table("users").select("username, nickname").in_("id", user_ids).execute()
    return [u["nickname"] if u["nickname"] else u["username"] for u in user_result.data]

def get_game_by_bgg_id(bgg_id: int):
    response = supabase.table("games").select("*").eq("bgg_id", bgg_id).execute()
    return response.data[0] if response.data else None

def get_users_with_game(game_id: int):
    response = supabase.table("users_games").select("user_id").eq("game_id", game_id).execute()
    return [entry["user_id"] for entry in response.data]

def get_users_by_ids(user_ids: list[int]):
    if not user_ids:
        return []
    response = supabase.table("users").select("username, nickname").in_("id", user_ids).execute()
    return response.data

def get_user_id_by_discord(discord_id: int):
    response = supabase.table("users").select("id").eq("discord_id", discord_id).execute()
    if response.data:
        return response.data[0]["id"]
    return None

def get_user_games_sorted_by_name(user_id: int) -> list[str]:
    result = supabase.table("users_games").select("game_id").eq("user_id", user_id).execute()
    game_ids = [link["game_id"] for link in result.data]
    if not game_ids:
        return []

    game_result = supabase.table("games").select("name").in_("id", game_ids).order("name").execute()
    return [g["name"] for g in game_result.data]

def get_or_create_user_id(discord_id: int, username: str, nickname: str = "") -> int:
    # Check if the user already exists
    result = supabase.table("users").select("id").eq("discord_id", discord_id).execute()
    if result.data:
        return result.data[0]["id"]

    # Create new user
    insert_result = supabase.table("users").insert({
        "discord_id": discord_id,
        "username": username,
        "nickname": nickname
    }).execute()

    return insert_result.data[0]["id"]

def get_user_games(user_id: int) -> list[dict]:
    """Returns a list of game records for the given user_id."""
    game_links = supabase.table("users_games").select("game_id").eq("user_id", user_id).execute()
    game_ids = [link["game_id"] for link in game_links.data]
    if not game_ids:
        return []

    games_result = supabase.table("games").select("id, name").in_("id", game_ids).execute()
    return games_result.data

def search_games_fuzzy(query: str, limit: int = 10) -> list:
    all_games = supabase.table("games").select("id, name").execute().data
    scored = [(g, fuzz.partial_ratio(query.lower(), g["name"].lower())) for g in all_games]
    top_matches = sorted(scored, key=lambda x: x[1], reverse=True)[:limit]
    return [g for g, _ in top_matches]


def create_session_entry(game_id: int, name: str = None, date: str = None):
    session_data = {"game_id": game_id}
    if name:
        session_data["name"] = name
    if date:
        session_data["date"] = date

    result = supabase.table("sessions").insert(session_data).execute()
    return result.data[0] if result.data else None

def get_all_registered_users() -> list[dict]:
    result = supabase.table("users").select("id, username, nickname").execute()
    return result.data

def link_user_to_session(session_id: int, user_id: int):
    result = supabase.table("sessions_users").insert({
        "session_id": session_id,
        "user_id": user_id
    }).execute()

    return result.data[0] if result.data else None

def get_sessions_for_game(game_id: int) -> list:
    result = supabase.table("sessions").select("*").eq("game_id", game_id).order("date", desc=True).execute()
    return result.data if result.data else []

def get_users_in_session(session_id: int) -> list[dict]:
    response = supabase.table("sessions_users").select("user_id").eq("session_id", session_id).execute()
    return response.data if response.data else []

