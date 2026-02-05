import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'player_stats.db') # Merging into main DB for simplicity or separate? Prompt said `db/skills.db`.
# "Create a separate table... for 'Unlocked Skills'. These are specialized buffs..."
# Prompt: "Step 2: The Skill Tree (db/skills.db) Create a separate table..." -> It explicitly says db/skills.db.
# I will create a new DB file for skills.

SKILLS_DB_PATH = os.path.join(os.path.dirname(__file__), 'skills.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'skills.sql')
MAIN_DB_PATH = os.path.join(os.path.dirname(__file__), 'player_stats.db')

def init_skills_db():
    conn = sqlite3.connect(SKILLS_DB_PATH)
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print(f"Skills Database initialized at {SKILLS_DB_PATH}")

    # Ensure Fatigue in Main DB
    conn_main = sqlite3.connect(MAIN_DB_PATH)
    cursor = conn_main.cursor()
    cursor.execute("INSERT OR IGNORE INTO player_stats (stat_name, value) VALUES ('Fatigue', 0)")
    conn_main.commit()
    conn_main.close()
    print("Fatigue stat ensured in Main DB.")

if __name__ == "__main__":
    init_skills_db()
