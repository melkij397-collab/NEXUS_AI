import os
import re
import sqlite3
from datetime import datetime, timezone


DB_PATH = "data/nexus_memory.db"


class NexusMemoryEngine:
    def __init__(self, user_id="default"):
        self.user_id = re.sub(
            r"[^a-zA-Z0-9_-]", "", str(user_id)
        )[:80] or "default"

        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.db_path = DB_PATH
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _initialize(self):
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    content TEXT NOT NULL,
                    source TEXT DEFAULT 'user',
                    confidence REAL DEFAULT 1.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_user
                ON memories(user_id)
            """)

    def add_fact(self, content, category="general"):
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Пустая запись")

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as db:
            cursor = db.execute("""
                INSERT INTO memories (
                    user_id, category, content,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.user_id,
                category,
                content.strip(),
                now,
                now
            ))

            return cursor.lastrowid

    def search_facts(self, query, limit=10):
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("""
                SELECT * FROM memories
                WHERE user_id = ? AND content LIKE ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (
                self.user_id,
                "%" + query + "%",
                limit
            )).fetchall()

            return [dict(row) for row in rows]

    def list_facts(self, limit=100):
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("""
                SELECT * FROM memories
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (self.user_id, limit)).fetchall()

            return [dict(row) for row in rows]

    def delete_fact(self, memory_id):
        with self._connect() as db:
            cursor = db.execute("""
                DELETE FROM memories
                WHERE id = ? AND user_id = ?
            """, (memory_id, self.user_id))

            return cursor.rowcount > 0

    def clear_facts(self):
        with self._connect() as db:
            db.execute(
                "DELETE FROM memories WHERE user_id = ?",
                (self.user_id,)
            )
