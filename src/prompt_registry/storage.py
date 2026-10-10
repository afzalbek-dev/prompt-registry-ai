import sqlite3
import time
import json
from typing import List, Dict, Any, Optional


class PromptStorage:
    """Promptlar va ularning baholash natijalarini SQLite bazasida saqlash."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    template TEXT NOT NULL,
                    variables TEXT NOT NULL,
                    model_target TEXT,
                    created_at REAL NOT NULL,
                    UNIQUE(name, version)
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    score REAL NOT NULL,
                    output TEXT,
                    latency_ms REAL,
                    notes TEXT,
                    evaluated_at REAL NOT NULL,
                    FOREIGN KEY(prompt_id) REFERENCES prompt_versions(id)
                )
                """
            )

    def save_prompt(self, name: str, template: str, variables: List[str], model: str = "default") -> int:
        cur = self._conn.cursor()
        cur.execute("SELECT MAX(version) FROM prompt_versions WHERE name = ?", (name,))
        latest_ver = cur.fetchone()[0] or 0
        new_ver = latest_ver + 1

        with self._conn:
            c = self._conn.execute(
                """
                INSERT INTO prompt_versions (name, version, template, variables, model_target, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, new_ver, template, json.dumps(variables), model, time.time()),
            )
            return c.lastrowid

    def get_prompt(self, name: str, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        cur = self._conn.cursor()
        if version is not None:
            cur.execute(
                """
                SELECT id, name, version, template, variables, model_target, created_at
                FROM prompt_versions
                WHERE name = ? AND version = ?
                """,
                (name, version),
            )
        else:
            cur.execute(
                """
                SELECT id, name, version, template, variables, model_target, created_at
                FROM prompt_versions
                WHERE name = ?
                ORDER BY version DESC LIMIT 1
                """,
                (name,),
            )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "version": row[2],
            "template": row[3],
            "variables": json.loads(row[4]),
            "model_target": row[5],
            "created_at": row[6],
        }

    def record_evaluation(self, prompt_id: int, score: float, output: str = "", latency_ms: float = 0.0, notes: str = ""):
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO prompt_evaluations (prompt_id, score, output, latency_ms, notes, evaluated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (prompt_id, score, output, latency_ms, notes, time.time()),
            )

    def get_evaluations(self, prompt_id: int) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT id, score, output, latency_ms, notes, evaluated_at
            FROM prompt_evaluations
            WHERE prompt_id = ?
            ORDER BY evaluated_at DESC
            """,
            (prompt_id,),
        )
        return [
            {
                "id": r[0],
                "score": r[1],
                "output": r[2],
                "latency_ms": r[3],
                "notes": r[4],
                "evaluated_at": r[5],
            }
            for r in cur.fetchall()
        ]

    def close(self):
        self._conn.close()
