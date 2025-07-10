# 🌪️ Squire

**Squire** is a powerful Discord bot for organizing board game nights. It helps communities manage collections, track sessions, and celebrate stats—all with seamless BoardGameGeek integration and Supabase as a backend.

---

## 🎯 Features

* 🧑‍💼 Register users with optional nicknames
* 🎲 Search and add games from [BoardGameGeek](https://boardgamegeek.com)
* 📚 View personal or shared game collections
* 📅 Create and manage play sessions with names & dates
* 👥 Add session participants and winners
* 📊 View user and game stats
* 🧠 Ask AI questions about game rules
* 🗑️ Delete sessions with confirmation
* 🏷️ Update your display nickname
* 📜 Paginated session history with winner display

---

## 🚀 Slash Commands

### 🧑 User Commands

* `/register_user [nickname]`
  Registers you in the system with an optional nickname.

* `/update_nickname <nickname>`
  Updates your display nickname.

### 🎲 Game Management

* `/add_game <query>`
  Search BoardGameGeek and add a game to your collection.

* `/remove_game <query>`
  Remove a game from your collection.

* `/owned_games [user]`
  Show your or another user’s board game collection.

* `/who_game <game>`
  Find out who owns a specific game.

* `/game_info <query>`
  View BGG data for a game and optionally add it to your collection (publicly visible).

### 📆 Session Management

* `/create_session <game_query>`
  Log a new game session by selecting a game, then entering a name and date.

* `/add_session_users <session_id>`
  Add players to a session via dropdown.

* `/add_winner <session_id>`
  Select and record winners for a session.

* `/list_sessions <game>`
  View a paginated list of sessions for a game, including winners and delete buttons.

* `/delete_session <session_id>`
  Delete a session after previewing its details.

### 🤖 AI Support

* `/ask_ai <question>`
  Ask an AI assistant about game rules (⚠️ AI-generated, use with discretion).

* `/user_stats [user]`
  View session wins and stats for yourself or another user.

* `/game_stats <query>`
  See how often a game has been played and its top winners.

---

## 🛠️ Setup

### 🔧 Prerequisites

* Python 3.11+
* Supabase project with the following tables:

  * `users`, `games`, `users_games`, `sessions`, `sessions_users`, `sessions_winners`, `users_servers`
* BoardGameGeek XML API access
* `.env` file with the following:

```env
DISCORD_TOKEN_DEV=your_dev_token
DISCORD_TOKEN_PROD=your_prod_token

SUPABASE_URL_DEV=https://your-dev.supabase.co
SUPABASE_KEY_DEV=your-dev-key

SUPABASE_URL_PROD=https://your-prod.supabase.co
SUPABASE_KEY_PROD=your-prod-key

OPEN_AI_DEV_KEY=your-openai-dev-key
OPEN_AI_PROD_KEY=your-openai-prod-key

GUILD_ID=your_discord_guild_id
GUILD_ID_2=your_optional_second_guild_id

ENV=dev|prod
```

---

### 🧪 Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### ▶️ Running the Bot

```bash
python bot.py
```

---

### 🖥️ Optional: Systemd Service

To run the bot as a background service:

1. Create a service file:

   ```ini
   [Unit]
   Description=Squire Bot
   After=network.target

   [Service]
   Type=simple
   WorkingDirectory=/path/to/your/project
   ExecStart=/path/to/your/project/.venv/bin/python bot.py
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

2. Save as `/etc/systemd/system/squire.service`, then:

```bash
sudo systemctl enable squire
sudo systemctl start squire
```

Check logs with:

```bash
journalctl -u squire -f
```

---

## 📝 Notes

* Interaction UIs (buttons/selects) timeout after 60 seconds.
* BGG game names are truncated to fit Discord UI limits.
* AI responses are for fun; verify against official rules for accuracy.

---

## 🗺 Roadmap

### 🔜 Short-Term

* 🎯 More slash command autocomplete
* 🏅 Global leaderboard and stat summaries
* 📤 Export session data

### 🧱 Mid-Term

* 🌐 Web dashboard for collection/session editing
* 📈 Charts and visual stats

### 🚀 Long-Term

* Multi-server hosting with user opt-in
* Auto-reminders for scheduled sessions

---

## 📄 License

MIT License © 2025 [Rane Wallin](https://github.com/ranewallin)
