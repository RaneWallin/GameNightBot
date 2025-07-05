# 🌪 Squire

Squire is a Discord bot designed to help communities manage board game collections, track play sessions, and coordinate game nights. It integrates with [BoardGameGeek](https://boardgamegeek.com) for game data and uses [Supabase](https://supabase.io) as its backend.

---

## 📦 Features

* 🔍 Search and add games from BGG
* 🎯 Find out who owns a game
* 📚 View and manage your collection
* 📝 Log play sessions
* 👥 Track session participants
* 🧠 Get game info with images and stats

---

## ✨ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/RaneWallin/GameNightBot.git
cd game-night-bot
```

### 2. Set Up a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up `.env`

Create a `.env` file in the root directory with the following contents:

```env
DISCORD_TOKEN=your_discord_bot_token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
GUILD_ID=your_discord_guild_id
```

---

## 🔑 Where to Find Supabase Keys

1. Go to [app.supabase.com](https://app.supabase.com) and open your project.
2. Navigate to **Settings > API**:

   * **SUPABASE\_URL** is your project’s URL (e.g., `https://abcxyz.supabase.co`)
   * **SUPABASE\_KEY** is the **Service Role** key (⚠️ Keep this secret and secure)
3. Copy both and paste them into your `.env` file.

---

## 🛠 Running the Bot

```bash
python bot.py
```

You should see:

```
🤖 Logged in as GameNightBot | Synced to guild 1234567890
```

---

## 📚 Command Highlights

| Command              | Description                            |
| -------------------- | -------------------------------------- |
| `/register_user`     | Register yourself in the system        |
| `/add_game`          | Add a game from BGG to your collection |
| `/find_game`         | See who owns a specific game           |
| `/my_games`          | View your collection                   |
| `/remove_game`       | Remove a game from your collection     |
| `/create_session`    | Log a game night session               |
| `/add_session_users` | Add users to a session (UI-based)      |
| `/list_sessions`     | List sessions where a game was played  |
| `/game_info`         | View BGG details and add the game      |

---

## 💡 Tips

* You must register before using most commands (`/register_user`)
* Only games in the Supabase database can be linked or played
* `/add_game` uses BGG’s XML API, so search results may vary slightly

---

## 📟 License

MIT License © 2025 Rane Wallin
