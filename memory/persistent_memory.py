import sqlite3
import json
from typing import List, Dict

DB_PATH = "memory/sessions.db"

class PersistentSessionMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            messages TEXT,
            confirmed INTEGER
        )
        """)

        cursor.execute("""
        INSERT OR IGNORE INTO sessions (session_id, messages, confirmed)
        VALUES (?, ?, ?)
        """, (self.session_id, json.dumps([]), 0))

        conn.commit()
        conn.close()

    def add(self, role: str, content: str, message_type: str = "message"):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT messages FROM sessions WHERE session_id = ?",
            (self.session_id,)
        )
        messages = json.loads(cursor.fetchone()[0])

        messages.append({
            "role": role,
            "content": content,
            "type": message_type
        })

        cursor.execute(
            "UPDATE sessions SET messages = ? WHERE session_id = ?",
            (json.dumps(messages), self.session_id)
        )

        conn.commit()
        conn.close()




    def get(self) -> List[Dict]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT messages FROM sessions WHERE session_id = ?",
            (self.session_id,)
        )
        messages = json.loads(cursor.fetchone()[0])

        conn.close()
        return messages

    def confirm(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE sessions SET confirmed = 1 WHERE session_id = ?",
            (self.session_id,)
        )

        conn.commit()
        conn.close()

    def is_confirmed(self) -> bool:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT confirmed FROM sessions WHERE session_id = ?",
            (self.session_id,)
        )
        confirmed = cursor.fetchone()[0]

        conn.close()
        return bool(confirmed)
    

    def get_last_assistant_message(self) -> str | None:
        messages = self.get()
        for msg in reversed(messages):
            if msg["role"] == "assistant":
                return msg["content"]
        return None
    
    def get_by_role(self, role: str) -> str | None:
        messages = self.get()
        for msg in reversed(messages):
            if msg["role"] == role:
                return msg["content"]
        return None
    
    def get_final_proposal(self) -> str | None:
        messages = self.get()
        for msg in reversed(messages):
            if msg.get("type") == "proposal":
                return msg["content"]
        return None




