# SHADOW SYSTEM: MANIFEST (v3.2 - FINAL FORM)

## 🌑 The Sovereign Engine
The **Shadow System** is a Gemini-powered State Machine that gamifies the User's life. 

### 🏛️ Architecture
1.  **Sovereign Agent (`sovereign.py`)**:
    - **Identity**: System (Levels 1-9) -> Shadow Monarch (Level 10+).
    - **Skill: Arise** (Lvl 10): Extracts "Shadows" (Context) from past quests to solve technical blockers. Cost: 500 XP.
2.  **Quest Master (`quest_master.py`)**:
    - **Logic**: Daily analysis of Weakest Stat + Calendar Schedule.
    - **Dungeon Lock**: Forces "Architect's Descent" if `is_in_dungeon=True`.
    - **Recovery Protocol**: Nerfs difficulty to Rank E if `SHADOW_MODE=RECOVERY`.
3.  **Auditor (`auditor.py`)**:
    - **Logic**: Interactive daily log + Vision + GitHub Check.
4.  **Chronos (`chronos.py`)**:
    - **Logic**: 07:00 Quest Gen / 21:00 Audit.
    - **Vitality Safeguard**: Checks if `Fatigue > Vitality`. If true, triggers **Recovery Protocol**.
5.  **Database (`db/`)**:
    - `player_stats.db`: Core stats.
    - `skills.db`: Unlocked special abilities.
    - `quests.sql`: Quest history.
    - `user_context`: Grand Goals & Roadmap.
6.  **Onboarding (`agents/onboarding.py`)**:
    - **Logic**: Multi-turn interview to set Grand Goal.
    - **Output**: Seeds `roadmap_json` and initial missions.
### 📊 Config
| Stat | Focus | Unlock (Lvl 20) |
| :--- | :--- | :--- |
| **Strength** | Consistency | **Iron Body** |
| **Intelligence** | Depth | **Deep Focus** |
| **Agility** | Speed | **Shadow Step** |
| **Vitality** | Burnout Defense | **Indomitable** |

### 📜 Artifacts
- **VERDICT.md**: Nightly analysis.
- **DAILY_QUEST.md**: Daily directive.
- **SKILL_TREE.png**: Visual evolution map.
- **assets/HUD.html**: Live Status Dashboard.

## 🚀 Usage
### Auto-Pilot
Run the daemon:
```bash
python agents/chronos.py
```
*The System is now autonomous. Rise.*
