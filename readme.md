# 🌪 Squire

Squire is a Discord bot designed to help communities manage board game collections, track play sessions, and coordinate game nights. It integrates with [BoardGameGeek](https://boardgamegeek.com) for game data and uses [Supabase](https://supabase.io) as its backend.

## Features

* Register users to the server
* Search and add games from BGG
* View your personal or others' game collections
* Create and log game sessions
* Add session participants and winners
* Ask AI questions about game rules

## Slash Commands

### `/register_user`

Registers you in the system. Optionally includes a nickname.

### `/add_game <query>`

Searches BGG and lets you add a game to your collection.

### `/owned_games [user]`

Displays the collection of the user who invoked the command, or another specified user.

### `/remove_game <query>`

Removes a game from your personal collection.

### `/create_session <game> [session_name] [session_date]`

Creates a session for a game you own.

### `/add_session_users <session_id>`

Interactive UI to add users to an existing session.

### `/add_winner <session_id>`

Interactive UI to select and log the winners of a session.

### `/list_sessions <game>`

Shows a list of sessions logged for a specific game.

### `/game_info <query>`

Displays BGG data and lets you add the game to your collection. Similar to /add_game but the game info is posted publicly, whereas /add_game is only seen by the specific user.

### `/who_game <game>`

Shows which users own a specific game.

### `/ask_ai <question>`

Uses OpenAI to answer questions about game rules (⚠️ AI generated, may be inaccurate).

## Setup

### Prerequisites

* Python 3.11+
* A Supabase project with tables:

  * `users`, `games`, `users_games`, `sessions`, `users_sessions`, `sessions_winners`, `users_servers`
* BoardGameGeek API (XML)
* `.env` file with:

  ```
  DISCORD_TOKEN=your_discord_token
  GUILD_ID=your_guild_id
  GUILD_ID_2=your_secondary_guild_id (optional)
  SUPABASE_URL=your_supabase_url
  SUPABASE_KEY=your_supabase_key
  OPENAI_API_KEY=your_openai_key
  ENV=prod|dev
  ```

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the Bot

```bash
python bot.py
```

### Systemd Setup (Optional)

Use `systemctl` to manage your bot as a background service.

### Logging

Use `journalctl -u your_service_name` to view logs.

## Notes

* Button and UI interactions timeout after 60 seconds.
* BGG search labels are truncated to fit Discord UI limits.
* AI answers should not be relied upon for serious rule debates.

## Roadmap

Short-Term Goals

* Add stats (i.e. most played games, most won, etc)

Mid-Term Goals

* Build a web interface

Long-Term Goals

* Host bot for other servers?

---

## 📟 License

MIT License © 2025 Rane Wallin
