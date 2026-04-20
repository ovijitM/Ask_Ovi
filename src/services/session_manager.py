import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional


class SessionManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL,
                    messages TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    memory_text TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT session_id, mode, messages, updated_at FROM chat_sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()

        if not row:
            return None

        return {
            "session_id": row[0],
            "mode": row[1],
            "messages": json.loads(row[2]),
            "updated_at": row[3],
        }

    def save_session(self, session_id: str, mode: str, messages: List[Dict[str, Any]]) -> None:
        payload = json.dumps(messages)
        now = datetime.utcnow().isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chat_sessions (session_id, mode, messages, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id)
                DO UPDATE SET mode=excluded.mode, messages=excluded.messages, updated_at=excluded.updated_at
                """,
                (session_id, mode, payload, now),
            )
            conn.commit()

    def clear_session(self, session_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
            conn.commit()

    def add_user_memory(self, user_id: str, memory_text: str) -> None:
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO user_memory (user_id, memory_text, created_at) VALUES (?, ?, ?)",
                (user_id, memory_text.strip(), now),
            )
            conn.commit()

    def get_user_memories(self, user_id: str, limit: int = 15) -> List[str]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT memory_text
                FROM user_memory
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()

        # Return oldest->newest for better model context readability.
        return [r[0] for r in reversed(rows)]

    def clear_user_memories(self, user_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM user_memory WHERE user_id = ?", (user_id,))
            conn.commit()
