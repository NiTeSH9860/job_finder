"""Tests for fit_scorer's pure logic: cosine similarity, verdict thresholds,
and keyword overlap. Does NOT test score_fit() itself, since that requires
loading the sentence-transformers model — see integration notes in README
for how to exercise that path manually.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.fit_scorer import (
    BORDERLINE_THRESHOLD,
    STRONG_THRESHOLD,
    _cosine_similarity,
    _overlapping_terms,
    _verdict_for_similarity,
)


def test_cosine_similarity_identical_vectors_is_one():
    v = np.array([1.0, 2.0, 3.0])
    assert _cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors_is_zero():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert _cosine_similarity(a, b) == pytest.approx(0.0)


def test_cosine_similarity_opposite_vectors_is_negative_one():
    a = np.array([1.0, 0.0])
    b = np.array([-1.0, 0.0])
    assert _cosine_similarity(a, b) == pytest.approx(-1.0)


def test_verdict_strong_at_and_above_threshold():
    assert _verdict_for_similarity(STRONG_THRESHOLD) == "strong"
    assert _verdict_for_similarity(STRONG_THRESHOLD + 0.1) == "strong"


def test_verdict_borderline_between_thresholds():
    midpoint = (STRONG_THRESHOLD + BORDERLINE_THRESHOLD) / 2
    assert _verdict_for_similarity(midpoint) == "borderline"


def test_verdict_poor_below_borderline_threshold():
    assert _verdict_for_similarity(BORDERLINE_THRESHOLD - 0.05) == "poor"


def test_overlapping_terms_finds_shared_keywords():
    posting = "We need someone skilled in python and sql for data analysis."
    resume = "Experienced in python, sql, and data visualization."
    overlap = _overlapping_terms(posting, resume)
    assert "python" in overlap
    assert "sql" in overlap


def test_overlapping_terms_excludes_stopwords():
    posting = "This role is for the team that will work with data."
    resume = "I have worked with the team on similar data projects."
    overlap = _overlapping_terms(posting, resume)
    assert "the" not in overlap
    assert "team" not in overlap  # stopword list includes "team"


def test_overlapping_terms_respects_top_n_limit():
    posting = "python sql java react aws docker kubernetes terraform golang rust"
    resume = "python sql java react aws docker kubernetes terraform golang rust"
    overlap = _overlapping_terms(posting, resume, top_n=3)
    assert len(overlap) == 3