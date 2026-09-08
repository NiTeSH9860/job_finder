"""Tools: log_application, needs_human_review

Persists what the agent did for each posting to a local SQLite database
(stdlib, zero extra setup for a judge running this fresh). Two tables:

- applications: one row per posting the agent acted on (drafted/applied/skipped)
- review_queue: postings flagged for the candidate's own judgment

needs_human_review is the tool that makes the agent run quietly and only
interrupt for real decisions — the core of the "handles it end to end,
only surfaces when there's a real decision" theme.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from strands import tool

DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    posting_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    notes TEXT,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS review_queue (
    posting_id TEXT PRIMARY KEY,
    reason TEXT NOT NULL,
    flagged_at TEXT NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 0
);
"""


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(_SCHEMA)
    return conn


@tool
def log_application(posting_id: str, status: str, notes: str = "") -> str:
    """Record what happened for a posting (drafted, applied, skipped, needs_review).

    Args:
        posting_id: The posting's id.
        status: One of "drafted", "applied", "skipped", "needs_review".
        notes: Optional free-text notes.

    Returns:
        Confirmation string.
    """
    now = datetime.now(timezone.utc).isoformat()
    with _get_connection() as conn:
        conn.execute(
            """INSERT INTO applications (posting_id, status, notes, updated_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(posting_id) DO UPDATE SET
                 status=excluded.status, notes=excluded.notes, updated_at=excluded.updated_at""",
            (posting_id, status, notes, now),
        )
    return f"Logged {posting_id} as {status}."


@tool
def needs_human_review(posting_id: str, reason: str) -> str:
    """Flag a posting for the candidate's own judgment instead of acting on it.

    Args:
        posting_id: The posting's id.
        reason: Why this needs a human decision (e.g. "pay below stated range",
                 "borderline seniority fit").

    Returns:
        Confirmation string.
    """
    now = datetime.now(timezone.utc).isoformat()
    with _get_connection() as conn:
        conn.execute(
            """INSERT INTO review_queue (posting_id, reason, flagged_at, resolved)
               VALUES (?, ?, ?, 0)
               ON CONFLICT(posting_id) DO UPDATE SET
                 reason=excluded.reason, flagged_at=excluded.flagged_at""",
            (posting_id, reason, now),
        )
    log_application(posting_id, "needs_review", reason)
    return f"Flagged {posting_id} for your review: {reason}"


def get_pending_reviews() -> list[dict]:
    """Helper (not an agent tool) for a future UI/CLI to list what's waiting on you."""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT posting_id, reason, flagged_at FROM review_queue WHERE resolved = 0"
        ).fetchall()
    return [{"posting_id": r[0], "reason": r[1], "flagged_at": r[2]} for r in rows]