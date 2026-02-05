import os
import sqlite3
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/player_stats.db')
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# The Sovereign's Interview Script
SYSTEM_INSTRUCTION = """
You are 'The Sovereign', an advanced AI System Gamification Engine. 
You are conducting an onboarding interview to initialize a new User.
Your tone is cold, authoritative, yet deeply insightful. You see through excuses.

The Interview consists of exactly 3 questions.
1. "What is your current rank/skill level in your primary domain? (Be honest, the System sees all)."
2. "What is the singular 'Great Quest' you must clear in the next 12 weeks? (e.g., Thesis, SC Exams, Job Offer)."
3. "What is your primary 'Shadow' (weakness)? (e.g., Burnout, Procrastination, Math)."

RULES:
- Ask ONE question at a time.
- Verify the user answers meaningfully. If they type gibberish, demand a proper answer.
- After the 3rd answer, say "ANALYSIS COMPLETE. INITIATING GENESIS..." and produce the JSON payload with `thinking_level="high"` analysis.
"""

def get_onboarding_history(session_id):
    """Retrieves chat history for a session (mocked for now, state is usually frontend-driven)."""
    # In a real app, we'd pull from a redis layer or DB. 
    # For now, we assume the frontend sends the history context.
    return []

def process_chat(history, user_input):
    """Processes the chat turn."""
    
    # 1. Prepare Chat
    model_id = "gemini-2.5-flash"
    
    # Convert history dicts to Content objects
    contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    
    contents.append(types.Content(role="user", parts=[types.Part(text=user_input)]))
    
    # 2. Resilience Protocol (Multi-Model Fallback)
    models_to_try = [
        "gemini-2.5-flash", 
        "gemini-2.0-flash", 
        "gemini-2.0-flash-lite-001"
    ]
    
    response = None
    last_error = None
    
    for model in models_to_try:
        try:
            print(f"--- ONBOARDING: Analyzing with {model} ---")
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="text/plain"
                )
            )
            break # Success, exit loop
        except Exception as e:
            print(f"Model Error ({model}): {e}")
            last_error = e
            # If rate limited, just try the next model immediately
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"Rate limit on {model}. Switching to next model...")
                continue
            else:
                # If it's a non-rate-limit error (e.g. invalid arg), maybe stop or try next? 
                # Let's try next to be safe.
                continue

    if not response:
        return {"error": f"All models exhausted. Last error: {str(last_error)}"}
        
    ai_reply = response.text
    
    # 3. Check for Completion Trigger
    # 3. Check for Completion Trigger
    if "INITIATING GENESIS" in ai_reply:
        # Clean the reply for the user (remove the raw JSON)
        user_reply_text = ai_reply.split("```json")[0].strip()
        if not user_reply_text:
            user_reply_text = "ANALYSIS COMPLETE. INITIATING GENESIS..."
            
        # We need to extract the JSON payload.
        # Let's ask Gemini to generate the structured data separately to ensure purity.
        genesis_data = generate_genesis_data(contents)
        
        return {
            "reply": user_reply_text,
            "genesis": genesis_data
        }

    if not response:
        # FALLBACK: OFFLINE BACKUP PROTOCOL
        print("CRITICAL: All models failed. Engaging Offline Backup Protocol.")
        return fallback_to_backup_protocol(history, user_input)
        
    ai_reply = response.text
    
    # 3. Check for Completion Trigger
    if "INITIATING GENESIS" in ai_reply:
        # Clean the reply for the user (remove the raw JSON)
        user_reply_text = ai_reply.split("```json")[0].strip()
        if not user_reply_text:
            user_reply_text = "ANALYSIS COMPLETE. INITIATING GENESIS..."
            
        # We need to extract the JSON payload.
        # Let's ask Gemini to generate the structured data separately to ensure purity.
        genesis_data = generate_genesis_data(contents)
        
        # Fallback for Genesis if Gemini fails there too
        if not genesis_data:
             genesis_data = get_mock_genesis_data()

        return {
            "reply": user_reply_text,
            "genesis": genesis_data
        }

    return {"reply": ai_reply}

def fallback_to_backup_protocol(history, user_input):
    """Rule-based responses when Gemini is down."""
    # History contains the full conversation including the current user message (if frontend sent it)
    # Plus we might have appended it again in 'contents' but here we look at raw history list.
    
    # Analyze Turn Count to guess state.
    # Turn 0: System Greeting (Model)
    # Turn 1: User Answer 1 (Rank)
    # Turn 2: System Q2 (Model)
    # Turn 3: User Answer 2 (Quest)
    # Turn 4: System Q3 (Model)
    # Turn 5: User Answer 3 (Shadow)
    
    # The 'history' list from frontend includes the latest user message.
    # So len(history) should be:
    # 2 -> User just answered Rank. Next: Ask Quest.
    # 4 -> User just answered Quest. Next: Ask Shadow.
    # 6 -> User just answered Shadow. Next: Genesis.
    
    turn_count = len(history)
    
    msg = "System Offline. Using Backup Protocol."
    
    if turn_count <= 2:
        msg = "Data received. Rank recorded. [BACKUP PROTOCOL]\n\nWhat is the singular 'Great Quest' you must clear in the next 12 weeks?"
    elif turn_count <= 4:
        msg = "Objective logged. [BACKUP PROTOCOL]\n\nWhat is your primary 'Shadow' (weakness)? (e.g. Burnout, Procrastination)."
    else:
        msg = "ANALYSIS COMPLETE. INITIATING GENESIS... (Offline Mode)"
        return {
            "reply": msg,
            "genesis": get_mock_genesis_data()
        }
        
    return {"reply": msg}

def get_mock_genesis_data():
    """Returns a safe default profile."""
    return {
        "grand_goal": "Survive the Shadow System",
        "shadow_weakness": "Rate Limits",
        "roadmap": {
            "Week 1": "System Calibration",
            "Week 2": "Basic Training",
            "Week 3": "Skill Acquisition",
            "Week 4": "First Dungeon",
            "Week 12": "Ascension"
        },
        "initial_quests": [
            {"title": "Bypass Limitations", "difficulty": "D", "reward_stat": "Intelligence"},
            {"title": "Manual Override", "difficulty": "E", "reward_stat": "Vitality"},
            {"title": "Persistence", "difficulty": "C", "reward_stat": "Strength"}
        ]
    }

def generate_genesis_data(chat_history):
    """Generates the seeding data based on the full interview."""
    print("--- INITIATING GENESIS ---")
    
    prompt = """
    Analyze the interview history.
    1. Map 'Great Quest' to `grand_goal`.
    2. Map 'Shadow' to `shadow_weakness`.
    3. Generate a 12-week roadmap (JSON Key-Value pairs of "Week X": "Focus").
    4. Generate 3 initial quests.
    
    Output JSON:
    {
        "grand_goal": "...",
        "shadow_weakness": "...",
        "roadmap": {"Week 1": "...", ...},
        "initial_quests": [
            {"title": "...", "difficulty": "D", "reward_stat": "Strength"}
        ]
    }
    """
    
    models_to_try = [
        "gemini-2.5-flash", 
        "gemini-2.0-flash", 
        "gemini-2.0-flash-lite-001"
    ]
    
    for model in models_to_try:
        try:
            print(f"--- GENESIS: Connecting with {model} ---")
            response = client.models.generate_content(
                model=model,
                contents=chat_history + [types.Content(role="user", parts=[types.Part(text=prompt)])],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return response.parsed
        except Exception as e:
            print(f"Genesis Error ({model}): {e}")
            continue
            
    print("FATAL: All models failed for Genesis.")
    return None

def seed_database(genesis_data):
    """Writes the genesis data to the DB."""
    if not genesis_data:
        return False
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. User Context
        cursor.execute("""
            INSERT INTO user_context (grand_goal, shadow_weakness, roadmap_json)
            VALUES (?, ?, ?)
        """, (
            genesis_data['grand_goal'],
            genesis_data['shadow_weakness'],
            json.dumps(genesis_data['roadmap'])
        ))
        
        # 2. Initial Quests
        for q in genesis_data['initial_quests']:
            cursor.execute("""
                INSERT INTO quests (title, description, difficulty, status, stat_reward_type, stat_reward_value, deadline)
                VALUES (?, ?, ?, 'ACTIVE', ?, ?, datetime('now', '+7 days'))
            """, (q['title'], "Genesis Mission", q['difficulty'], q['reward_stat'], 2))
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"DB Seeding Error: {e}")
        return False
