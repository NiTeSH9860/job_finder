"""Tests for the tracker tool: SQLite-backed logging and review queue."""

import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def tracker(tmp_path, monkeypatch):
    """Fresh tracker module with its DB pointed at a temp file per test."""
    import tools.tracker as tracker_module

    monkeypatch.setattr(tracker_module, "DB_PATH", tmp_path / "test_tracker.db")
    importlib.reload(tracker_module)  # in case DB_PATH is read at import time elsewhere
    monkeypatch.setattr(tracker_module, "DB_PATH", tmp_path / "test_tracker.db")
    return tracker_module


def test_log_application_creates_record(tracker):
    result = tracker.log_application("posting-1", "drafted", "first pass")
    assert "posting-1" in result
    assert "drafted" in result


def test_log_application_upserts_on_same_id(tracker):
    tracker.log_application("posting-1", "drafted")
    tracker.log_application("posting-1", "applied", "sent it")

    with tracker._get_connection() as conn:
        row = conn.execute(
            "SELECT status, notes FROM applications WHERE posting_id = ?", ("posting-1",)
        ).fetchone()
    assert row == ("applied", "sent it")


def test_needs_human_review_adds_to_queue(tracker):
    tracker.needs_human_review("posting-2", "pay below stated range")
    pending = tracker.get_pending_reviews()
    assert len(pending) == 1
    assert pending[0]["posting_id"] == "posting-2"
    assert pending[0]["reason"] == "pay below stated range"


def test_needs_human_review_also_logs_application(tracker):
    """Flagging for review should be visible in the applications table too."""
    tracker.needs_human_review("posting-3", "unusual seniority ask")
    with tracker._get_connection() as conn:
        row = conn.execute(
            "SELECT status FROM applications WHERE posting_id = ?", ("posting-3",)
        ).fetchone()
    assert row == ("needs_review",)


def test_get_pending_reviews_only_returns_unresolved(tracker):
    tracker.needs_human_review("posting-4", "reason a")
    with tracker._get_connection() as conn:
        conn.execute(
            "UPDATE review_queue SET resolved = 1 WHERE posting_id = ?", ("posting-4",)
        )
    assert tracker.get_pending_reviews() == []


def test_multiple_postings_tracked_independently(tracker):
    tracker.log_application("a", "drafted")
    tracker.log_application("b", "skipped")
    tracker.needs_human_review("c", "borderline fit")

    with tracker._get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    assert count == 3