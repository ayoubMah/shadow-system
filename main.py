import argparse
import sys
import sqlite3
import os
from agents.auditor import run_audit

DB_PATH = os.path.join(os.path.dirname(__file__), 'db/player_stats.db')

def generate_hud(stats_for_hud, profile_for_hud):
    """Generates the HUD.html file."""
    level, xp, job_class, is_in_dungeon = profile_for_hud
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shadow System HUD</title>
        <style>
            body {{ background-color: #0d0d0d; color: #4285F4; font-family: 'Courier New', monospace; padding: 20px; }}
            .container {{ border: 2px solid #4285F4; padding: 20px; max-width: 600px; margin: auto; box-shadow: 0 0 20px #4285F4; }}
            h1 {{ text-align: center; text-transform: uppercase; letter-spacing: 5px; }}
            .stat-row {{ display: flex; justify-content: space-between; border-bottom: 1px solid #333; padding: 5px 0; }}
            .value {{ color: white; }}
            .alert {{ color: red; font-weight: bold; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Shadow System</h1>
            <div class="stat-row"><span>Class</span><span class="value">{job_class}</span></div>
            <div class="stat-row"><span>Level</span><span class="value">{level}</span></div>
            <div class="stat-row"><span>XP</span><span class="value">{xp} / {level * 1000}</span></div>
            <br>
            <h3>Attributes</h3>
    """
    for stat_name, value in stats_for_hud:
        html += f'<div class="stat-row"><span>{stat_name}</span><span class="value">{value}</span></div>'
    
    if is_in_dungeon:
        html += '<p class="alert">⚠️ INSIDE DUNGEON</p>'
        
    html += """
        </div>
    </body>
    </html>
    """
    
    hud_path = os.path.join(os.path.dirname(__file__), 'assets/HUD.html')
    os.makedirs(os.path.dirname(hud_path), exist_ok=True)
    with open(hud_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HUD Generated at {hud_path}")

def check_stats():
    """Displays current player stats and generates HUD."""
    if not os.path.exists(DB_PATH):
        print("Error: Database not found. Please run initialization first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get Profile
    cursor.execute("SELECT level, xp, job_class, is_in_dungeon FROM player_profile WHERE id=1")
    profile = cursor.fetchone()
    
    # Get Stats
    cursor.execute("SELECT stat_name, value FROM player_stats")
    stats = cursor.fetchall()

    print("\n--- 📊 PLAYER STATUS ---")
    if profile:
        print(f"Name: Ayoub")
        print(f"Class: {profile[2]}")
        print(f"Level: {profile[0]} (XP: {profile[1]})")
        if profile[3]: # is_in_dungeon
            print("🛑 STATE: DUNGEON ACTIVE")
    
    print("-" * 20)
    for stat_name, value in stats:
        print(f"{stat_name}: {value}")
    print("-" * 20)
    
    if profile:
        generate_hud(stats, profile)
    else:
        print("Warning: Player profile not found, HUD not generated.")
        
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Shadow System: The Sovereign Engine")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Audit Command
    subparsers.add_parser("audit", help="Run the nightly audit sequence")
    
    # Stats Command
    subparsers.add_parser("stats", help="View current player stats")
    subparsers.add_parser("status", help="View current player stats")
    
    args = parser.parse_args()
    
    if args.command == "audit":
        run_audit()
    elif args.command == "stats" or args.command == "status":
        check_stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
