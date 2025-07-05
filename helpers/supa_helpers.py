import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from thefuzz import fuzz
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from config import SUPABASE_URL, SUPABASE_KEY


# Load .env config
load_dotenv()

# Validate environment variables
REQUIRED_ENV_VARS = ["SUPABASE_URL", "SUPABASE_KEY"]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

# Initialize client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=ClientOptions(schema="public"))

# -----------------------
# USER HELPERS
# -----------------------

def create_user(discord_id, username, nickname="") -> int:
    existing = supabase.table("users").select("id").eq("discord_id", discord_id).execute()
    if existing.data:
        return existing.data[0]
    inserted = supabase.table("users").insert({
        "discord_id": discord_id,
        "username": username,
        "nickname": nickname
    }).execute()
    return inserted.data[0]

def get_user_by_id(user_id):
    user = supabase.table("users").select("*").eq("id", user_id).execute()
    if user.data:
        return user.data[0]
    return None

def get_user_by_discord_id(discord_id: int) -> Optional[Dict[str, Any]]:
    result = supabase.table("users").select("*").eq("discord_id", discord_id).execute()
    return result.data[0] if result.data else None

# def get_user_id_by_discord(discord_id: int) -> Optional[int]:
#     result = supabase.table("users").select("id").eq("discord_id", discord_id).execute()
#     return result.data[0]["id"] if result.data else None

def get_all_registered_users() -> List[Dict[str, Any]]:
    return supabase.table("users").select("id, username, nickname").execute().data

# def create_user(discord_id: int, username: str, nickname: str = "") -> bool:
#     result = supabase.table("users").insert({
#         "discord_id": discord_id,
#         "username": username,
#         "nickname": nickname
#     }).execute()
#     return bool(result.data)

# def get_or_create_user_id(discord_id: int, username: str, nickname: str = "") -> int:
#     existing = supabase.table("users").select("id").eq("discord_id", discord_id).execute()
#     if existing.data:
#         return existing.data[0]["id"]
#     created = supabase.table("users").insert({
#         "discord_id": discord_id,
#         "username": username,
#         "nickname": nickname
#     }).execute()
#     return created.data[0]["id"]

def register_user_to_server(user_id: int, server_id: int) -> int:
    existing = supabase.table('users_servers').select('*').eq('user_id', user_id).eq('server_id', server_id).execute()
    if existing.data:
        return existing.data[0]["id"]
    created = supabase.table("users_servers").insert({
        "user_id": user_id,
        "server_id": server_id
    }).execute()
    return created.data[0]["id"]

# -----------------------
# GAME HELPERS
# -----------------------

def get_or_create_game(bgg_id: int, game_data: dict) -> int:
    existing = supabase.table("games").select("id").eq("bgg_id", bgg_id).execute()
    if existing.data:
        return existing.data[0]["id"]
    inserted = supabase.table("games").insert({
        "bgg_id": bgg_id,
        "name": game_data["name"],
        "publisher": game_data["publisher"],
        "designer": game_data["designer"],
        "min_players": game_data["min_players"],
        "max_players": game_data["max_players"]
    }).execute()
    return inserted.data[0]["id"]

def find_game_by_bgg_id(bgg_id: int) -> Optional[dict]:
    result = supabase.table("games").select("id, name").eq("bgg_id", bgg_id).execute()
    return result.data[0] if result.data else None

def get_game_by_bgg_id(bgg_id: int):
    result = supabase.table("games").select("*").eq("bgg_id", bgg_id).execute()
    return result.data[0] if result.data else None

def get_games_by_ids(game_ids: List[int]) -> List[Dict[str, Any]]:
    if not game_ids:
        return []
    result = supabase.table("games").select("id, name").in_("id", game_ids).order("name").execute()
    return result.data

def search_games_fuzzy(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    all_games = supabase.table("games").select("id, name").execute().data
    scored = [(g, fuzz.partial_ratio(query.lower(), g["name"].lower())) for g in all_games]
    top_matches = sorted(scored, key=lambda x: x[1], reverse=True)[:limit]
    return [g for g, _ in top_matches]

# -----------------------
# COLLECTION HELPERS
# -----------------------

def user_has_game(user_id: int, game_id: int) -> bool:
    result = supabase.table("users_games").select("*").eq("user_id", user_id).eq("game_id", game_id).execute()
    return bool(result.data)

def link_user_game(user_id: int, game_id: int):
    if user_has_game(user_id, game_id):
        return  # Avoid duplicates
    supabase.table("users_games").insert({
        "user_id": user_id,
        "game_id": game_id
    }).execute()

def remove_game_link(user_id: int, game_id: int):
    supabase.table("users_games").delete().eq("user_id", user_id).eq("game_id", game_id).execute()

def get_owned_game_ids(user_id: int) -> List[int]:
    result = supabase.table("users_games").select("game_id").eq("user_id", user_id).execute()
    return [r["game_id"] for r in result.data]

def get_user_games_sorted_by_name(user_id: int) -> List[str]:
    game_ids = get_owned_game_ids(user_id)
    if not game_ids:
        return []
    result = supabase.table("games").select("name").in_("id", game_ids).order("name").execute()
    return [g["name"] for g in result.data]

def get_user_games(user_id: int) -> List[Dict[str, Any]]:
    game_ids = get_owned_game_ids(user_id)
    if not game_ids:
        return []
    result = supabase.table("games").select("id, name").in_("id", game_ids).execute()
    return result.data

def search_user_games_by_name(user_id: int, query: str) -> List[Dict[str, Any]]:
    return [g for g in get_user_games(user_id) if query.lower() in g["name"].lower()]

def find_users_with_game(game_id: int) -> List[str]:
    result = supabase.table("users_games").select("user_id").eq("game_id", game_id).execute()
    user_ids = [u["user_id"] for u in result.data]
    if not user_ids:
        return []
    users = supabase.table("users").select("username, nickname").in_("id", user_ids).execute()
    return [u["nickname"] or u["username"] for u in users.data]

def get_users_with_game(game_id: int) -> List[int]:
    result = supabase.table("users_games").select("user_id").eq("game_id", game_id).execute()
    return [r["user_id"] for r in result.data]

def get_users_by_ids(user_ids: List[int]) -> List[Dict[str, Any]]:
    if not user_ids:
        return []
    result = supabase.table("users").select("username, nickname").in_("id", user_ids).execute()
    return result.data

# -----------------------
# SESSION HELPERS
# -----------------------

def create_session_entry(game_id: int, name: Optional[str] = None, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
    data = {"game_id": game_id}
    if name: data["name"] = name
    if date: data["date"] = date
    result = supabase.table("sessions").insert(data).execute()
    return result.data[0] if result.data else None

def get_sessions_for_game(game_id: int) -> List[Dict[str, Any]]:
    result = supabase.table("sessions").select("*").eq("game_id", game_id).order("date", desc=True).execute()
    return result.data or []

def link_user_to_session(session_id: int, user_id: int):
    # Prevent duplicates
    existing = supabase.table("sessions_users").select("*").eq("session_id", session_id).eq("user_id", user_id).execute()
    if existing.data:
        return
    supabase.table("sessions_users").insert({
        "session_id": session_id,
        "user_id": user_id
    }).execute()

def get_users_in_session(session_id: int) -> List[Dict[str, Any]]:
    result = supabase.table("sessions_users").select("user_id").eq("session_id", session_id).execute()
    return result.data or []

def link_winner_to_session(session_id: int, user_id: int):
    # Assuming 'supabase' is a pre-configured Supabase client
    supabase.from_("sessions_winners").insert({"session_id": session_id, "user_id": user_id}).execute()

def get_session_by_id(session_id: int):
    return supabase.from_("sessions").select("*").eq("id", session_id).single()

def get_winners_in_session(session_id: int) -> List[Dict[str, Any]]:
    result = supabase.table("sessions_winners").select("user_id").eq("session_id", session_id).execute()
    return result.data or []
