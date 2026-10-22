import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from app.config import BKT_P_INIT, DATABASE_PATH


def get_db_path(db_path: Optional[Path] = None) -> Path:
    """Resolves target database path: explicit argument > DB_PATH env var > VERCEL env var > DATABASE_PATH."""
    if db_path is not None:
        return Path(db_path)
    env_db = os.getenv("DB_PATH", "").strip()
    if env_db:
        return Path(env_db)
    if os.getenv("VERCEL"):
        return Path("/tmp/cognify.db")
    return DATABASE_PATH


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Returns a SQLite connection with row factory configured."""
    target_path = get_db_path(db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
    except sqlite3.OperationalError:
        conn.execute("PRAGMA journal_mode = DELETE;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """Initializes tables in the SQLite database if they do not exist."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS student_mastery (
                student_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                p_known REAL NOT NULL DEFAULT 0.3,
                total_attempts INTEGER NOT NULL DEFAULT 0,
                correct_attempts INTEGER NOT NULL DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (student_id, concept_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                selected_option INTEGER NOT NULL,
                is_correct BOOLEAN NOT NULL,
                misconception TEXT,
                p_known_before REAL NOT NULL,
                p_known_after REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_responses_student ON responses(student_id);
            CREATE INDEX IF NOT EXISTS idx_responses_concept ON responses(concept_id);
            CREATE INDEX IF NOT EXISTS idx_responses_misconception ON responses(misconception);
            CREATE INDEX IF NOT EXISTS idx_mastery_student ON student_mastery(student_id);

            CREATE TABLE IF NOT EXISTS misconception_explanations_cache (
                cache_key TEXT PRIMARY KEY,
                question_id TEXT NOT NULL,
                selected_option INTEGER NOT NULL,
                misconception TEXT NOT NULL,
                explanation TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_cache_question_opt ON misconception_explanations_cache(question_id, selected_option);
            """)
    finally:
        conn.close()


def create_or_get_student(student_id: str, name: Optional[str] = None, db_path: Optional[Path] = None) -> dict:
    """Ensures a student exists in SQLite, creating them if not present."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)

            student_name = name or f"Student {student_id}"
            cursor.execute(
                "INSERT INTO students (student_id, name) VALUES (?, ?)",
                (student_id, student_name),
            )
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            return dict(row)
    finally:
        conn.close()


def get_student_mastery_map(student_id: str, db_path: Optional[Path] = None) -> Dict[str, float]:
    """Returns a dict mapping concept_id -> p_known for a given student."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT concept_id, p_known FROM student_mastery WHERE student_id = ?",
            (student_id,),
        )
        rows = cursor.fetchall()
        return {row["concept_id"]: float(row["p_known"]) for row in rows}
    finally:
        conn.close()


def get_student_concept_stats(student_id: str, concept_id: str, db_path: Optional[Path] = None) -> dict:
    """Returns mastery row for a specific student and concept, or default initial values."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM student_mastery WHERE student_id = ? AND concept_id = ?",
            (student_id, concept_id),
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {
            "student_id": student_id,
            "concept_id": concept_id,
            "p_known": BKT_P_INIT,
            "total_attempts": 0,
            "correct_attempts": 0,
        }
    finally:
        conn.close()


def record_response_and_update_mastery(
    student_id: str,
    question_id: str,
    concept_id: str,
    selected_option: int,
    is_correct: bool,
    misconception: Optional[str],
    p_known_before: float,
    p_known_after: float,
    db_path: Optional[Path] = None,
) -> int:
    """
    Atomically records the student response and updates the BKT mastery record in SQLite.
    Returns the inserted response ID.
    """
    create_or_get_student(student_id, db_path=db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO responses 
                (student_id, question_id, concept_id, selected_option, is_correct, misconception, p_known_before, p_known_after, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_id,
                    question_id,
                    concept_id,
                    selected_option,
                    1 if is_correct else 0,
                    misconception,
                    p_known_before,
                    p_known_after,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            response_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO student_mastery (student_id, concept_id, p_known, total_attempts, correct_attempts, last_updated)
                VALUES (?, ?, ?, 1, ?, ?)
                ON CONFLICT(student_id, concept_id) DO UPDATE SET
                    p_known = excluded.p_known,
                    total_attempts = student_mastery.total_attempts + 1,
                    correct_attempts = student_mastery.correct_attempts + excluded.correct_attempts,
                    last_updated = excluded.last_updated
                """,
                (
                    student_id,
                    concept_id,
                    p_known_after,
                    1 if is_correct else 0,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            return response_id
    finally:
        conn.close()


def get_all_students(db_path: Optional[Path] = None) -> List[dict]:
    """Returns all students in the database."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY student_id ASC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_mastery_matrix(db_path: Optional[Path] = None) -> List[dict]:
    """Returns all rows in student_mastery."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_mastery")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_misconception_records(db_path: Optional[Path] = None) -> List[dict]:
    """Returns aggregated misconception counts and detailed records."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT misconception, concept_id, COUNT(*) as count, COUNT(DISTINCT student_id) as affected_students
            FROM responses
            WHERE is_correct = 0 AND misconception IS NOT NULL AND misconception != ''
            GROUP BY misconception, concept_id
            ORDER BY count DESC
            """
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_student_answered_question_ids(student_id: str, db_path: Optional[Path] = None) -> Set[str]:
    """Returns the set of question IDs that this student has answered."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT question_id FROM responses WHERE student_id = ?",
            (student_id,),
        )
        rows = cursor.fetchall()
        return {row["question_id"] for row in rows}
    finally:
        conn.close()


def get_student_misconceptions(student_id: str, db_path: Optional[Path] = None) -> List[dict]:
    """Returns top misconceptions recorded for a specific student."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT misconception, concept_id, COUNT(*) as count
            FROM responses
            WHERE student_id = ? AND is_correct = 0 AND misconception IS NOT NULL AND misconception != ''
            GROUP BY misconception, concept_id
            ORDER BY count DESC
            """,
            (student_id,),
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_cached_misconception_explanation(cache_key: str, db_path: Optional[Path] = None) -> Optional[dict]:
    """Retrieves cached misconception explanation by cache_key from SQLite."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM misconception_explanations_cache WHERE cache_key = ?",
            (cache_key,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def save_cached_misconception_explanation(
    cache_key: str,
    question_id: str,
    selected_option: int,
    misconception: str,
    explanation: str,
    source: str = "llm",
    db_path: Optional[Path] = None,
) -> None:
    """Persists a generated misconception explanation into SQLite cache."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO misconception_explanations_cache
                (cache_key, question_id, selected_option, misconception, explanation, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    explanation = excluded.explanation,
                    source = excluded.source,
                    created_at = excluded.created_at
                """,
                (
                    cache_key,
                    question_id,
                    selected_option,
                    misconception,
                    explanation,
                    source,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
    finally:
        conn.close()


def get_all_cached_misconceptions(db_path: Optional[Path] = None) -> List[dict]:
    """Returns all cached misconception explanations."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM misconception_explanations_cache ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def clean_test_students(db_path: Optional[Path] = None) -> int:
    """
    Deletes all students whose id or name starts with 'test_', 'demo_student', or 'Student test_'
    from the database, along with their mastery and answer records.
    Returns the count of deleted students.
    """
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT student_id FROM students 
                WHERE student_id LIKE 'test_%' 
                   OR student_id LIKE 'demo_student%' 
                   OR name LIKE 'Student test_%'
                   OR name LIKE 'test_%'
                   OR name LIKE 'demo_student%'
                """
            )
            rows = cursor.fetchall()
            st_ids = [r["student_id"] for r in rows]
            if not st_ids:
                return 0

            placeholders = ",".join("?" for _ in st_ids)
            cursor.execute(f"DELETE FROM responses WHERE student_id IN ({placeholders})", st_ids)
            cursor.execute(f"DELETE FROM student_mastery WHERE student_id IN ({placeholders})", st_ids)
            cursor.execute(f"DELETE FROM students WHERE student_id IN ({placeholders})", st_ids)
            return len(st_ids)
    finally:
        conn.close()


