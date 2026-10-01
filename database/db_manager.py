import sqlite3
import os
import chromadb
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), 'execution_logs.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')
CHROMA_PATH = os.path.join(os.path.dirname(__file__), 'vector_store')

def init_db():
    """Initialize the SQLite database with the schema."""
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())

def insert_log(prompt: str, tokens: int, execution_time: float, test_status: str) -> int:
    """Insert a new execution log and return its ID."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO execution_logs (prompt, tokens, execution_time, test_status) VALUES (?, ?, ?, ?)',
            (prompt, tokens, execution_time, test_status)
        )
        return cursor.lastrowid

def get_logs() -> List[Dict[str, Any]]:
    """Retrieve all execution logs."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM execution_logs ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]

def get_chroma_client():
    """Returns an initialized local persistent ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_PATH)

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
