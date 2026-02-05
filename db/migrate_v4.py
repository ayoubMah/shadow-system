import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'player_stats.db')

def migrate_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE player_profile ADD COLUMN is_in_dungeon BOOLEAN DEFAULT 0")
        conn.commit()
        print("Successfully added 'is_in_dungeon' column.")
    except sqlite3.OperationalError as e:
        print(f"Migration might have already run or error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
