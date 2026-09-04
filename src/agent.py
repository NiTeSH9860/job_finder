"""
Job Application Agent — Strands Agents SDK orchestrator.

The agent loop: search for new postings -> score fit against the resume ->
draft tailored materials for strong fits -> log everything -> surface only
the postings that need a human judgment call (borderline fit, unusual ask).

Run:
    python src/agent.py
"""

from strands import Agent

from tools.job_search import search_postings
from tools.fit_scorer import score_fit
from tools.drafter import draft_materials
from tools.tracker import log_application, needs_human_review


SYSTEM_PROMPT = """You are a job-search agent working on behalf of one candidate.
Your job each run:
1. Call search_postings to pull new listings matching the candidate's criteria.
2. For each new posting, call score_fit to evaluate it against the candidate's resume.
3. If the fit is clearly strong, call draft_materials to produce tailored resume
   bullets and a cover letter, then call log_application to record it.
4. If the fit is borderline, or something about the posting is unusual
   (pay below range, odd requirements, senior stretch role), call
   needs_human_review instead of drafting anything — do NOT guess on the
   candidate's behalf for judgment calls.
5. Never fabricate postings, scores, or company details. Only act on what
   the tools return.
Be concise in your summaries back to the candidate."""


def build_agent() -> Agent:
    return Agent(
        system_prompt=SYSTEM_PROMPT,
        tools=[search_postings, score_fit, draft_materials, log_application, needs_human_review],
    )


def run_once(candidate_profile: dict) -> str:
    """Single pass of the agent loop. Call this on a schedule (cron, AgentCore, etc.)."""
    agent = build_agent()
    prompt = (
        f"Candidate resume summary: {candidate_profile['resume_summary']}\n"
        f"Target roles: {candidate_profile['target_roles']}\n"
        f"Locations: {candidate_profile['locations']}\n"
        "Run one full search-score-draft-log cycle now."
    )
    result = agent(prompt)
    return str(result)


if __name__ == "__main__":
    # Replace with the real candidate profile, or load from a config/env file.
    demo_profile = {
        "resume_summary": "Entry-level data scientist, Python, scikit-learn, LLM/RAG projects.",
        "target_roles": ["Data Scientist", "Data Analyst"],
        "locations": ["Remote", "Kathmandu, Nepal"],
    }
    print(run_once(demo_profile))