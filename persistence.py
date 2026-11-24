"""Local SQLite persistence for learner profiles and progress."""

import json
import os
import sqlite3
from pathlib import Path


DEFAULT_STATE = {
    "learner_profile": {
        "level": "Intermediate",
        "goal": "",
        "explanation_style": "Balanced",
        "diagnostic_completed": False,
        "diagnostic_score": 0,
        "diagnostic_total": 0,
    },
    "quiz_score": 0,
    "quiz_total": 0,
    "quiz_difficulty": "Medium",
    "quiz_correct_streak": 0,
    "quiz_question_number": 0,
    "topic_performance": {},
    "quiz_history": [],
    "learner_mastery": {},
    "conversation_counts": {},
}


class SQLiteStateStore:
    """Persist one local learner profile without external services."""

    def __init__(self, database_path=None, profile_id=None):
        self.database_path = Path(
            database_path
            or os.getenv(
                "LEARNLENS_STATE_DB",
                Path(__file__).with_name("learnlens.db"),
            )
        )
        self.profile_id = (
            profile_id
            or os.getenv("LEARNLENS_PROFILE_ID", "local")
        ).strip() or "local"

    def _connect(self):
        connection = sqlite3.connect(str(self.database_path))
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS learner_state (
                profile_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS video_transcripts (
                cache_key TEXT NOT NULL,
                model_size TEXT NOT NULL,
                chunks_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (cache_key, model_size)
            )
            """
        )
        return connection

    def save(self, state):
        serialized = json.dumps(state, ensure_ascii=False)
        connection = self._connect()
        try:
            with connection:
                connection.execute(
                    """
                    INSERT INTO learner_state (profile_id, state_json)
                    VALUES (?, ?)
                    ON CONFLICT(profile_id) DO UPDATE SET
                        state_json = excluded.state_json,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (self.profile_id, serialized),
                )
        finally:
            connection.close()

    def load(self):
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT state_json
                FROM learner_state
                WHERE profile_id = ?
                """,
                (self.profile_id,),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        state = json.loads(row[0])
        return state if isinstance(state, dict) else None

    def save_video_transcript(self, cache_key, model_size, chunks):
        connection = self._connect()
        try:
            with connection:
                connection.execute(
                    """
                    INSERT INTO video_transcripts
                        (cache_key, model_size, chunks_json)
                    VALUES (?, ?, ?)
                    ON CONFLICT(cache_key, model_size) DO UPDATE SET
                        chunks_json = excluded.chunks_json,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        cache_key,
                        model_size,
                        json.dumps(chunks, ensure_ascii=False),
                    ),
                )
        finally:
            connection.close()

    def load_video_transcript(self, cache_key, model_size):
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT chunks_json
                FROM video_transcripts
                WHERE cache_key = ? AND model_size = ?
                """,
                (cache_key, model_size),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        chunks = json.loads(row[0])
        return chunks if isinstance(chunks, list) else None
