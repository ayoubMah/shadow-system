import os
import sqlite3
import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from agents.calendar_sync import fetch_todays_events, block_time_for_deep_work

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/player_stats.db')
DAILY_QUEST_PATH = os.path.join(os.path.dirname(__file__), '../DAILY_QUEST.md')
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_lowest_stat():
    """Finds the player's lowest stat to prioritize."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT stat_name, value FROM player_stats ORDER BY value ASC LIMIT 1")
        stat = cursor.fetchone()
        conn.close()
        return stat if stat else ("Strength", 10) # Default
    except Exception:
        return ("Strength", 10)

def create_quest_entry(title, description, difficulty, stat_reward_type, stat_reward_value):
    """Writes the quest to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quests (title, description, difficulty, status, stat_reward_type, stat_reward_value, deadline)
        VALUES (?, ?, ?, 'ACTIVE', ?, ?, ?)
    """, (title, description, difficulty, stat_reward_type, stat_reward_value, datetime.datetime.now().replace(hour=23, minute=59).isoformat()))
    conn.commit()
    conn.close()

def save_daily_quest(content):
    with open(DAILY_QUEST_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Quest Artifact saved to {DAILY_QUEST_PATH}")
    
def generate_daily_quest():
    """Generates a quest based on stats and schedule."""
    print("--- ⚔️ QUEST MASTER: INITIATING SEQUENCE ⚔️ ---")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check Dungeon State
    cursor.execute("SELECT is_in_dungeon, job_class FROM player_profile WHERE id=1")
    row = cursor.fetchone()
    if row and row[0]: # is_in_dungeon is True
        print("⚔️ DUNGEON DETECTED ⚔️")
        print("Protocol Locked: 'The Architect's Descent'")
        quest_text = """# ⛩️ DAILY QUEST: THE ARCHITECT'S DESCENT
**Status**: LOCKED (Dungeon Active)
**Objective**: Survival.
1. Complete a microservice module.
2. Complete 100 Sambo Throws.
**Penalty for Failure**: Stat Reset.
"""
        save_daily_quest(quest_text)
        conn.close()
        return

    conn.close()

    # 1. Analyze State
    lowest_stat_name, lowest_stat_val = get_lowest_stat()
    print(f"Weakness Detected: {lowest_stat_name} (Level {lowest_stat_val})")
    
    events = fetch_todays_events()
    schedule_context = "; ".join(events) if events else "Schedule is clear."

    # Check for Recovery Mode
    is_recovery = os.getenv("SHADOW_MODE") == "RECOVERY"
    if is_recovery:
        print("🛡️ VITALITY SAFEGUARD ACTIVE. Nerfing Quest Difficulty.")
        lowest_stat_name = "Vitality" # Force Vitality focus
        prompt_override = "Generate a Rank E 'Recovery Quest' (Sleep, Stretch, Walk). STRICTLY LOW INTENSITY."
    else:
        prompt_override = ""

    # 2. Gemini Reasoning
    prompt = f"""
    You are the Quest Master for the Shadow System.
    User's Weakness: {lowest_stat_name}.
    Schedule: {schedule_context}.
    {prompt_override}
    
    Generate a 'Daily Quest' to address this weakness.
    - If Strength is low: 'Leg Day' or 'Sambo Drills'.
    - If Intelligence is low: 'Deep Code' or 'Thesis Sprint'.
    - If Vitality is low: 'Sleep' or 'Meditation'.
    
    Output JSON format:
    {{
        "title": "Quest Title",
        "description": "Short forceful description",
        "difficulty": "Rank (E, D, C, B, A, S)",
        "stat_reward_type": "{lowest_stat_name}",
        "stat_reward_value": 2,
        "calendar_event_name": "[QUEST] Title"
    }}
    """
    import time

    retries = 3
    response = None
    
    for attempt in range(retries):
        try:
            print(f"--- QUEST MASTER: Consulting the Oracle (Attempt {attempt+1}/{retries}) ---")
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            break
        except Exception as e:
            print(f"Gemini Error (Attempt {attempt+1}): {e}")
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < retries - 1:
                    print("Rate limit hit. Sleeping 10s...")
                    time.sleep(10)
                    continue
            raise e
            
    if not response:
        raise Exception("Failed to get response.")
    
    import json
    try:
        quest_data = response.parsed
        if not quest_data:
            print("DEBUG: response.parsed is None. Attempting manual parse.")
            print(f"DEBUG: Raw Text: {response.text}")
            quest_data = json.loads(response.text)
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        # Fallback default quest if parsing fails completely
        quest_data = {
            "title": "System Reboot",
            "description": "The Oracle spoke in riddles. Perform manual diagnostics.",
            "difficulty": "E",
            "stat_reward_type": "Intelligence",
            "stat_reward_value": 1,
            "calendar_event_name": "[QUEST] System Reboot"
        }
    
    # 3. Execution
    print(f"New Quest: {quest_data['title']} ({quest_data['difficulty']})")
    
    # Save to DB
    create_quest_entry(
        quest_data['title'], 
        quest_data['description'], 
        quest_data['difficulty'], 
        quest_data['stat_reward_type'], 
        quest_data['stat_reward_value']
    )
    
    print(f"Quest added to Quest Log.")

    # 4. Generate Artifact
    artifact_content = f"""# 📜 DAILY QUEST
**Target**: {quest_data['title']}
**Rank**: {quest_data['difficulty']}
**Objective**: {quest_data['description']}
**Reward**: +{quest_data['stat_reward_value']} {quest_data['stat_reward_type']}

---
*System generated based on weakness: {lowest_stat_name}*
"""
    save_daily_quest(artifact_content)

if __name__ == "__main__":
    generate_daily_quest()
