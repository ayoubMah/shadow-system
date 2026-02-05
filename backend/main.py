from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
from pydantic import BaseModel

app = FastAPI(title="Shadow System API", version="1.0.0")

# CORS config for Next.js (usually runs on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db/player_stats.db')

# Models
class Stat(BaseModel):
    name: str
    value: int

class Profile(BaseModel):
    level: int
    xp: int
    job_class: str
    is_in_dungeon: bool

# Helpers
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    return {"system": "Shadow Sovereign", "status": "ONLINE"}

@app.get("/status")
def get_status():
    """Returns the full player status (Stats + Profile)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Profile
        cursor.execute("SELECT level, xp, job_class, is_in_dungeon FROM player_profile WHERE id=1")
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile = {
            "level": row["level"],
            "xp": row["xp"],
            "job_class": row["job_class"],
            "is_in_dungeon": bool(row["is_in_dungeon"])
        }
        
        # Stats
        cursor.execute("SELECT stat_name, value FROM player_stats")
        stats = {row["stat_name"]: row["value"] for row in cursor.fetchall()}
        
        # Active Quest
        cursor.execute("SELECT title, description, difficulty, stat_reward_type, stat_reward_value, deadline FROM quests WHERE status='ACTIVE' ORDER BY id DESC LIMIT 1")
        quest_row = cursor.fetchone()
        quest = None
        if quest_row:
            quest = {
                "title": quest_row["title"],
                "description": quest_row["description"],
                "difficulty": quest_row["difficulty"],
                "reward": f"+{quest_row['stat_reward_value']} {quest_row['stat_reward_type']}",
                "deadline": quest_row["deadline"]
            }
            
        # User Context (Genesis Data)
        cursor.execute("SELECT grand_goal, shadow_weakness, roadmap_json FROM user_context ORDER BY id DESC LIMIT 1")
        context_row = cursor.fetchone()
        context = None
        if context_row:
            import json
            roadmap = {}
            try:
                roadmap = json.loads(context_row["roadmap_json"])
            except:
                roadmap = {}
                
            context = {
                "grand_goal": context_row["grand_goal"],
                "shadow_weakness": context_row["shadow_weakness"],
                "roadmap": roadmap
            }
        
        return {"profile": profile, "stats": stats, "quest": quest, "context": context}
        
    finally:
        conn.close()

# Awakening Protocol
class AwakenRequest(BaseModel):
    goals: str

@app.post("/awaken")
def awaken_system(request: AwakenRequest):
    """Initializes the System with a custom User Class based on goals."""
    from google import genai
    from google.genai import types
    from dotenv import load_dotenv
    
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    print(f"Awakening requested: {request.goals}")
    
    import time
    import json

    # 1. Gemini Analysis
    prompt = f"""
    User Goals: "{request.goals}"
    
    Task: Create a "Solo Leveling" style Job Class Name for this user.
    - Software Engineer -> "Code Necromancer" or "Shadow Architect"
    - Gym Bro -> "Iron Titan" or "Monarch of Force"
    - Hybrid -> "Techno-Paladin" or "Algorithm Strider"
    
    Output JSON: {{ "job_class": "Class Name" }}
    """
    
    retries = 3
    for attempt in range(retries):
        try:
            print(f"Attempt {attempt+1}/{retries} connecting to Gemini...")
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            print(f"DEBUG: Raw Gemini Response: {response.text}")
            
            if response.parsed:
                result = response.parsed
            else:
                # Fallback manual parse
                result = json.loads(response.text)
                
            new_class = result.get('job_class', 'Shadow Candidate')
            break # Success
        except Exception as e:
            print(f"Gemini Error (Attempt {attempt+1}): {e}")
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < retries - 1:
                    print("Rate limit hit. Sleeping 5s...")
                    time.sleep(5)
                    continue
            new_class = "Shadow Candidate" # Fallback on final failure or non-retryable error

    # 2. Update DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE player_profile SET job_class = ? WHERE id=1", (new_class,))
    conn.commit()
    conn.close()
    
    return {"status": "AWAKENED", "new_class": new_class}

# Onboarding Chat Protocol
class ChatRequest(BaseModel):
    history: list # List of {role: user/model, content: str}
    message: str

@app.post("/onboarding/chat")
def onboarding_chat(request: ChatRequest):
    """Handles the multi-turn onboarding interview."""
    from agents.onboarding import process_chat, seed_database
    
    response = process_chat(request.history, request.message)
    
    # If Genesis triggered, seed DB
    if "genesis" in response:
        success = seed_database(response["genesis"])
        response["genesis_status"] = "SUCCESS" if success else "FAILURE"
        
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
