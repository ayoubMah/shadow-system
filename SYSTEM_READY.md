# SYSTEM READY - SHADOW SOVEREIGN

## 🌑 System Status: ONLINE
The Multi-Agent Framework is successfully deployed.

### 🏛️ Agent Roster
1.  **Sovereign Engine (`agents/sovereign.py`)**:
    - **Model**: Gemini 2.0 Flash Thinking (Simulated Gemini 3 Pro).
    - **Capabilities**: High-level reasoning, Stat Balancing, Fatigue Penalty, Verdict Generation.
    - **Artifacts**: Generates `VERDICT.md` after every audit.
2.  **Auditor (`agents/auditor.py`)**:
    - **Capabilities**: Interactive daily log collection, Google Calendar scanning.
3.  **Calendar Gateway (`agents/calendar_sync.py`)**:
    - **Capabilities**: Event fetching, Time blocking.

### 💾 Data Layer
- **Database**: `db/player_stats.db` (Initialized).
- **Schema**: Includes `player_stats`, `player_profile`, `quests`, `quest_log`, `audit_logs`.

## 🚀 How to Initialize
1.  **Check Credentials**: Ensure `credentials.json` is in `shadow-system/` for Calendar access.
2.  **Verify Stats**:
    ```bash
    python main.py stats
    ```

## ⚔️ The Nightly Protocol
Execute the following command every night at 21:00:
```bash
python main.py audit
```

### What happens?
1.  **Scanner**: The system sees you missed "Sambo".
2.  **Interrogation**: It asks *why*.
3.  **Judgment**:
    - If "Fatigue": Checks if you slept well. Maybe -50 XP but +1 Rest.
    - If "Laziness": -1 Strength, -100 XP.
4.  **Verdict**: A `VERDICT.md` file is generated with the Sovereign's decree.

---
*"I am the architect of my own destruction... and my own rebirth."*
