CREATE TABLE IF NOT EXISTS execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    tokens INTEGER,
    execution_time REAL,
    test_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
