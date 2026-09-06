"""Tool: score_fit

Scores a posting against the candidate's resume using Sentence-BERT
embeddings + cosine similarity — the same approach used in the
resume-job-matcher project this agent builds on.

Deterministic and cheap (no LLM call per posting), which matters once
the agent is scoring dozens of postings per run.

Model loads once at import time and is reused across calls.
"""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer
from strands import tool

_MODEL_NAME = "all-MiniLM-L6-v2"

# Verdict thresholds — tune these against real postings once you have data;
# these starting values assume raw cosine similarity roughly in [0.2, 0.8]
# for related-but-not-identical text, which is typical for this model.
STRONG_THRESHOLD = 0.55
BORDERLINE_THRESHOLD = 0.40


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(_MODEL_NAME)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _overlapping_terms(posting_description: str, resume_summary: str, top_n: int = 5) -> list[str]:
    """Cheap keyword overlap for a human-readable rationale (not used for scoring)."""
    stopwords = {
        "the", "and", "for", "with", "you", "your", "our", "are", "will",
        "this", "that", "have", "has", "job", "role", "work", "team", "a",
        "to", "of", "in", "on", "is", "as", "an", "or", "be", "we",
    }
    posting_words = {w.strip(".,()").lower() for w in posting_description.split()}
    resume_words = {w.strip(".,()").lower() for w in resume_summary.split()}
    overlap = (posting_words & resume_words) - stopwords
    return sorted(w for w in overlap if len(w) > 2)[:top_n]


@tool
def score_fit(posting_description: str, resume_summary: str) -> dict:
    """Score how well a posting fits the candidate's resume.

    Args:
        posting_description: The job posting's description text.
        resume_summary: A summary of the candidate's resume/skills.

    Returns:
        dict with keys: score (0-100), verdict ("strong" | "borderline" | "poor"),
        rationale (one sentence).
    """
    model = _get_model()
    posting_vec, resume_vec = model.encode([posting_description, resume_summary])
    similarity = _cosine_similarity(posting_vec, resume_vec)
    score = round(max(0.0, min(1.0, similarity)) * 100)

    if similarity >= STRONG_THRESHOLD:
        verdict = "strong"
    elif similarity >= BORDERLINE_THRESHOLD:
        verdict = "borderline"
    else:
        verdict = "poor"

    overlap = _overlapping_terms(posting_description, resume_summary)
    rationale = (
        f"Overlapping terms: {', '.join(overlap)}."
        if overlap
        else "Low term overlap between posting and resume summary."
    )

    return {"score": score, "verdict": verdict, "rationale": rationale}