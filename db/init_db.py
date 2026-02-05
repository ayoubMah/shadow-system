import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'player_stats.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'quests.sql')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
