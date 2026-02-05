# Shadow System - Architecture & Implementation Overview

## 🌑 The Vision
The **Shadow System** is a "Solo Leveling"-inspired personal management engine. It treats the user as a "Player" with RPG stats (Strength, Intelligence, etc.) and uses **Gemini 3** (The Sovereign) as the Game Master to analyze daily progress, assign quests, and manage evolution.

## 🏛️ Architecture

The system follows a modular agentic architecture:

```mermaid
graph TD
    User((User)) -->|Daily Logs| Auditor[Auditor Agent]
    Calendar[(Google Calendar)] -->|Events| Auditor
    Auditor -->|Structured Log| Sovereign[Sovereign Agent (Gemini)]
    Sovereign -->|Function Call| DB[(SQLite DB)]
    Sovereign -->|Feedback| User
```

### 1. The Sovereign Engine (`agents/sovereign.py`)
- **Role**: The Brain / Game Master.
- **Tech**: Google Gemini API.
- **Logic**:
    - Receives daily activity logs.
    - Uses "High" thinking level to reason about trade-offs (e.g., studying vs. training).
    - Calls the `update_player_stats` tool to modify the database.
    - Returns a "System Verdict" in the persona of the Shadow Sovereign.

### 2. The Auditor (`agents/auditor.py`)
- **Role**: The Interface / Nightly Check-in.
- **Logic**:
    - Fetches the day's schedule from Google Calendar.
    - Interactively asks the user about completion ("Did you do Sambo?").
    - Captures reasons for failure ("Burnout", "Injury").
    - Compiles a report for the Sovereign.

### 3. The Calendar Proxy (`agents/calendar_sync.py`)
- **Role**: The Eyes.
- **Tech**: Google Calendar API.
- **Logic**:
    - Fetches events to inform the Auditor.
    - (Future) Can block time for "Deep Work" quests.

### 4. Semantic Memory (`db/`)
- **Tech**: SQLite.
- **Schema**:
    - `player_stats`: Stores RPG attributes (Strength, Agility, Intelligence).
    - `player_profile`: Tracks Level, XP, and Class.
    - `audit_logs`: Historical record of system interactions.

## 🛠️ Implementation Details

### File Structure
```
shadow-system/
├── agents/
│   ├── sovereign.py       # Gemini integration & Tool definitions
│   ├── auditor.py         # CLI interaction loop
│   └── calendar_sync.py   # Calendar API wrapper
├── db/
│   ├── player_stats.db    # SQLite database
│   ├── quests.sql         # Schema definition
│   └── init_db.py         # Initialization script
├── main.py                # Entry point (CLI)
├── .env                   # API Keys
└── requirements.txt       # Dependencies
```

### Key Workflows
1.  **Initialization**: `init_db.py` creates the schema and seeds default stats.
2.  **Nightly Audit**:
    - User runs `python main.py audit`.
    - System fetches calendar events.
    - User confirms/denies completion.
    - Gemini evaluates performance and updates stats (e.g., +1 Intelligence for coding, -1 Vitality for skipping rest).
3.  **Stat Logic**:
    - Stats are persistent.
    - Changes are logged with a "Reason" to track growth over time.
