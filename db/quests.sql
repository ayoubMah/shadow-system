-- Table for Player Stats
CREATE TABLE IF NOT EXISTS player_stats (
    stat_name TEXT PRIMARY KEY,
    value INTEGER DEFAULT 0
);

-- Table for Player Profile (Level, XP, etc.)
CREATE TABLE IF NOT EXISTS player_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    job_class TEXT DEFAULT 'None',
    is_in_dungeon BOOLEAN DEFAULT 0
);

-- Table for Quests
CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    difficulty TEXT, -- E, D, C, B, A, S
    status TEXT DEFAULT 'ACTIVE', -- ACTIVE, COMPLETED, FAILED
    deadline DATETIME,
    stat_reward_type TEXT,
    stat_reward_value INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table for Quest Completion History (Audit Logs linked to specific quests if needed, or just general history)
CREATE TABLE IF NOT EXISTS quest_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_name TEXT NOT NULL,
    status TEXT NOT NULL, -- COMPLETED, FAILED, PARTIAL
    notes TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table for Daily Logs (Audit History)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE DEFAULT (DATE('now')),
    content TEXT,
    audit_result TEXT
);

-- Insert default stats if not exists
INSERT OR IGNORE INTO player_profile (id, level, xp, job_class) VALUES (1, 1, 0, 'Shadow Monarch Candidate');
INSERT OR IGNORE INTO player_stats (stat_name, value) VALUES ('Strength', 10);
INSERT OR IGNORE INTO player_stats (stat_name, value) VALUES ('Agility', 10);
INSERT OR IGNORE INTO player_stats (stat_name, value) VALUES ('Intelligence', 10);
INSERT OR IGNORE INTO player_stats (stat_name, value) VALUES ('Vitality', 10);
INSERT OR IGNORE INTO player_stats (stat_name, value) VALUES ('Sense', 10);
