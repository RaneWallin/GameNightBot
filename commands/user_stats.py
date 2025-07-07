from discord import Interaction
from helpers.supa_helpers import (
    get_user_by_discord_id,
    get_sessions_for_game,
    get_users_in_session,
    get_winners_in_session,
    get_game_by_id,
    get_all_games
)


def get_total_sessions_played(user_id: int, all_sessions: list[dict]) -> int:
    return sum(
        user_id in [u["user_id"] for u in get_users_in_session(s["id"])]
        for s in all_sessions
    )


def get_total_wins(user_id: int, all_sessions: list[dict]) -> int:
    return sum(
        user_id in [w["user_id"] for w in get_winners_in_session(s["id"])]
        for s in all_sessions
    )


def get_most_played_game(user_id: int, all_sessions: list[dict]) -> tuple[str, int]:
    game_counts = {}
    for session in all_sessions:
        if any(u["user_id"] == user_id for u in get_users_in_session(session["id"])):
            game_id = session["game_id"]
            game_counts[game_id] = game_counts.get(game_id, 0) + 1

    if not game_counts:
        return ("N/A", 0)

    most_played_game_id = max(game_counts, key=game_counts.get)
    game_data = get_game_by_id(most_played_game_id)
    return (game_data["name"], game_counts[most_played_game_id])


def get_all_sessions(server_id: int) -> list[dict]:
    sessions = []
    seen_ids = set()

    all_games = get_all_games()
    for game in all_games:
        game_sessions = get_sessions_for_game(game["id"], server_id)
        for s in game_sessions:
            if s["id"] not in seen_ids:
                seen_ids.add(s["id"])
                sessions.append(s)

    return sessions


async def handle_user_stats(interaction: Interaction, user=None):
    await interaction.response.defer(ephemeral=False)

    if user is None:
        user = interaction.user

    db_user = get_user_by_discord_id(user.id, interaction.guild_id)
    if not db_user:
        await interaction.followup.send("❌ User not found. Use `/register_user` to register.", ephemeral=True)
        return

    user_id = db_user["id"]
    all_sessions = get_all_sessions(interaction.guild_id)

    total_sessions = get_total_sessions_played(user_id, all_sessions)
    total_wins = get_total_wins(user_id, all_sessions)
    most_played_name, most_played_count = get_most_played_game(user_id, all_sessions)

    await interaction.followup.send(
        f"📊 **Stats for {user.mention}**\n"
        f"• 🎮 Sessions played: **{total_sessions}**\n"
        f"• 🏆 Wins: **{total_wins}**\n"
        f"• 🔁 Most played: **{most_played_name}** ({most_played_count}x)",
        ephemeral=False
    )
