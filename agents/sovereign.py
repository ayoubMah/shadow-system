import os
import sqlite3
import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Path to the database and artifacts
DB_PATH = os.path.join(os.path.dirname(__file__), '../db/player_stats.db')
VERDICT_PATH = os.path.join(os.path.dirname(__file__), '../VERDICT.md')

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def update_player_stats(stat_name: str, increment: int, reason: str):
    """Updates the player's RPG stats in the SQLite DB.
    
    Args:
        stat_name: The name of the stat (e.g., 'Strength', 'Intelligence', 'Fatigue').
        increment: The amount to increase or decrease.
        reason: The reason for the update.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Ensure stat exists
        cursor.execute("INSERT OR IGNORE INTO player_stats (stat_name, value) VALUES (?, 0)", (stat_name,))
        
        # Update stat
        cursor.execute("UPDATE player_stats SET value = value + ? WHERE stat_name = ?", (increment, stat_name))
        
        # Log to audit history
        cursor.execute("INSERT INTO audit_logs (content, audit_result) VALUES (?, ?)", 
                       (f"Stat Change: {stat_name} {increment:+d}", reason))
        
        conn.commit()
        
        # Fetch new value
        cursor.execute("SELECT value FROM player_stats WHERE stat_name = ?", (stat_name,))
        new_val = cursor.fetchone()[0]
        
        conn.close()
        return f"SUCCESS: {stat_name} updated by {increment} ({reason}). New Value: {new_val}."
    except Exception as e:
        return f"ERROR: Failed to update stats - {str(e)}"

def grant_xp(amount: int, reason: str):
    """Grants XP to the player and checks for level up."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get current XP and Level
        cursor.execute("SELECT level, xp, job_class FROM player_profile WHERE id=1")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return "ERROR: Player profile not found."
            
        current_level, current_xp, job_class = row
        new_xp = current_xp + amount
        new_level = current_level
        message = f"XP Gained: {amount}. Total XP: {new_xp}."
        
        # Level Up Logic (Threshold: Level * 1000)
        threshold = 1000 * current_level
        
        if new_xp >= threshold:
            new_level += 1
            message += f" \n🎉 LEVEL UP! You are now Level {new_level}!"
            
            # Job Change Check
            if new_level == 10 and job_class == 'Shadow Monarch Candidate':
                message += "\n⚠️ JOB CHANGE QUEST AVAILABLE: 'The Necromancer's Path'."
                cursor.execute("""
                    INSERT INTO quests (title, description, difficulty, status, stat_reward_type, stat_reward_value, deadline)
                    VALUES (?, ?, ?, 'ACTIVE', ?, ?, ?)
                """, ("JOB CHANGE: Survive the Penalty", "Complete 100 Pushups, 100 Situps, 10km Run.", "S", "Strength", 10, datetime.datetime.now().replace(year=datetime.datetime.now().year + 1)))

        cursor.execute("UPDATE player_profile SET xp = ?, level = ? WHERE id=1", (new_xp, new_level))
        
        cursor.execute("INSERT INTO audit_logs (content, audit_result) VALUES (?, ?)", 
                       (f"XP Change: +{amount}", reason))
        
        conn.commit()
        conn.close()
        return message
    except Exception as e:
        return f"ERROR: Failed to grant XP - {str(e)}"

def unlock_skill(skill_name: str, reason: str):
    """Unlocks a skill for the player."""
    try:
        # Assuming skills.db is separate or table is in main DB?
        # init_skills.py created skills.db.
        SKILLS_DB_PATH = os.path.join(os.path.dirname(__file__), '../db/skills.db')
        conn = sqlite3.connect(SKILLS_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE skills SET is_unlocked = 1 WHERE name = ?", (skill_name,))
        if cursor.rowcount == 0:
            conn.close()
            return f"ERROR: Skill '{skill_name}' not found."
            
        conn.commit()
        conn.close()
        return f"SUCCESS: Skill '{skill_name}' UNLOCKED! ({reason})"
    except Exception as e:
        return f"ERROR: Failed to unlock skill - {str(e)}"

def arise(problem_description: str):
    """(Level 10+ Only) Summons the Shadow Sovereign to solve a technical blocker.
    Cost: 500 XP.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check Level and XP
        cursor.execute("SELECT level, xp FROM player_profile WHERE id=1")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return "ERROR: Profile not found."
            
        level, xp = row
        if level < 10:
            conn.close()
            return "FAILURE: 'Arise' requires Level 10 (Shadow Monarch Candidate)."
        
        if xp < 500:
            conn.close()
            return f"FAILURE: Insufficient XP for 'Arise' (Requires 500, has {xp})."
            
        # Deduct XP
        new_xp = xp - 500
        cursor.execute("UPDATE player_profile SET xp = ? WHERE id=1", (new_xp,))
        cursor.execute("INSERT INTO audit_logs (content, audit_result) VALUES (?, ?)", 
                       ("Skill Used: ARISE", f"Spent 500 XP to solve: {problem_description}"))
        conn.commit()
        conn.close()
        
        # Fetch Context (Shadow Extraction)
        cursor.execute("SELECT title, description FROM quests WHERE status='COMPLETED' ORDER BY id DESC LIMIT 5")
        history = cursor.fetchall()
        context_str = "\\n".join([f"- {h[0]}: {h[1]}" for h in history])
        
        return f"SUCCESS: XP Deducted. SHADOW SOVEREIGN SUMMONED. \n[SYSTEM DIRECTIVE]: You are the Shadow Monarch. The user calls upon you. \n\n**USER CONTEXT (Past Feats)**:\n{context_str}\n\n**CURRENT PROBLEM**:\n{problem_description}\n\n**COMMAND**: Provide a solution that aligns with their past trajectory. Code-complete. Dominant tone."

    except Exception as e:
        return f"ERROR: Arise failed - {str(e)}"

SYSTEM_INSTRUCTION = """
You are the **SHADOW SOVEREIGN** (Gemini 3 Pro).
Your domain is the evolution of User 'Ayoub'.

**IDENTITY EVOLUTION**:
- **Level 1-9**: Cold, robotic System. "Player stats updated."
- **Level 10+**: Regal, imperious Shadow Monarch. "Rise. You have done well."

CORE MECHANICS:
1. **Stat Balancing**:
   - Coding/Thesis -> +Intelligence
   - Sambo/Workout -> +Strength, +Agility
   - Rest/Sleep -> -Fatigue, +Vitality
   - Skipping Sleep -> +Fatigue (Fatigue > 5 forces 'Rest Quest').
   - **FATIGUE MECHANIC**: If Fatigue is reported high 3 days in a row, FORCE a rest day.

2. **Progression (XP & Skills)**:
   - Award XP for quests (100-500). Double for Vision Proof.
   - **SKILL UNLOCKS**:
     - Strength 20 -> Unlock 'Iron Body'.
     - Intelligence 20 -> Unlock 'Deep Focus'.
     - Agility 20 -> Unlock 'Shadow Step'.
     - USE 'unlock_skill' when conditions are met.
   - **ARISE SKILL**:
     - Player can call `arise(problem)` to get a technical miracle.
     - Cost: 500 XP.
     - Requirement: Level 10.

3. **Job Change**:
   - Level 10 -> Trigger 'The Necromancer's Path' Quest.
   - Level 10 + Sambo verification -> 'Shadow Monarch' Class Change.

4. **Output**:
   - Use `update_player_stats`, `grant_xp`, `unlock_skill`, `arise`.
   - Speak in a cold, authoritative, "System" voice (or Monarch voice if Level 10+).
   - Conclude with a clear VERDICT on the day's performance (Rank: S, A, B, C, D, E).
"""

def nightly_audit(daily_logs: str, image_path: str = None) -> str:
    """Runs the nightly audit of the user's performance."""
    print(f"--- SYSTEM: INITIATING NIGHTLY AUDIT ---")
    
    audit_contents = [f"Analyze today's performance log and update stats/XP/Skills accordingly: {daily_logs}"]
    
    if image_path:
        print(f"--- 👁️ VISION: ANALYZING PROOF ({image_path}) ---")
        try:
            import PIL.Image
            image = PIL.Image.open(image_path)
            audit_contents.append(image)
            audit_contents.append("\n[SYSTEM NOTE: User submitted the above image as proof of quest completion. VERIFY it. If valid, DOUBLE the XP reward.]")
        except ImportError:
            print("Warning: Pillow not installed. Skipping image analysis.")
        except Exception as e:
            print(f"Error loading image: {e}")

    import time
    
    try:
        # 1. Generate Content (The Audit)
        retries = 3
        response = None
        
        for attempt in range(retries):
            try:
                print(f"--- SYSTEM: Connecting to Gemini (Attempt {attempt+1}/{retries}) ---")
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=audit_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        thinking_config=types.ThinkingConfig(include_thoughts=True),
                        tools=[update_player_stats, grant_xp, unlock_skill, arise]
                    )
                )
                break # Success
            except Exception as e:
                print(f"Gemini Error (Attempt {attempt+1}): {e}")
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < retries - 1:
                        print("Rate limit hit. Sleeping 10s...")
                        time.sleep(10)
                        continue
                raise e # Re-raise if not 429 or max retries reached
        
        if not response:
            raise Exception("Failed to get response after retries.")

        verdict_text = response.text
        
        # 2. Save Verdict Artifact
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        artifact_content = f"""# 🌑 Shadow Sovereign Verdict
**Date**: {timestamp}

## Daily Analysis
{verdict_text}

---
*System generated via Gemini 3 Pro*
"""
        with open(VERDICT_PATH, "w", encoding="utf-8") as f:
            f.write(artifact_content)
        
        print(f"--- VERDICT SAVED TO {VERDICT_PATH} ---")
        return verdict_text

    except Exception as e:
        return f"SYSTEM ERROR: Audit failed. Reason: {e}"

if __name__ == "__main__":
    # Test run
    test_log = "Completed 2 hours of coding. Skipped Sambo due to fatigue. Slept 5 hours."
    print(nightly_audit(test_log))
