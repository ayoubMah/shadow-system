-- Table for Skills
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    unlock_condition TEXT, -- e.g., "Strength >= 20"
    effect TEXT,
    is_unlocked BOOLEAN DEFAULT 0
);

-- Pre-populate some skills
INSERT OR IGNORE INTO skills (name, description, unlock_condition, effect) VALUES 
('Iron Body', 'Reduces XP loss from physical fatigue by 50%.', 'Strength >= 20', 'XP_PENALTY_REDUCTION_50'),
('Deep Focus', 'Grants 1.5x XP for Intelligence quests completed before noon.', 'Intelligence >= 20', 'INT_XP_BOOST_1.5'),
('Shadow Step', 'Allows skipping one daily quest per week without penalty.', 'Agility >= 20', 'SKIP_PENALTY_WAIVER');
