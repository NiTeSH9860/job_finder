"""Tool: draft_materials

Generates tailored resume bullets and a short cover letter for a posting
the agent has already decided is a strong fit. Uses Google's genai SDK
(consistent with the model used in the candidate's prior LLM projects).

Requires GOOGLE_API_KEY in your environment (see .env.example).
"""

import json
import os

from google import genai
from google.genai import types
from strands import tool

_MODEL_NAME = "gemini-2.0-flash"

_DRAFT_PROMPT = """You are helping a job candidate tailor their application materials.

Candidate resume summary:
{resume_summary}

Job posting:
{posting_description}

Write:
1. Three tailored resume bullet points that highlight the candidate's most
   relevant experience for THIS posting specifically. Do not invent
   experience the candidate doesn't have — only reframe/reorder what's in
   the resume summary to match the posting's language.
2. A concise cover letter (3 short paragraphs max) for this specific role.
"""

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "tailored_bullets": {"type": "array", "items": {"type": "string"}},
        "cover_letter": {"type": "string"},
    },
    "required": ["tailored_bullets", "cover_letter"],
}


def _get_client() -> genai.Client:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GOOGLE_API_KEY. Add it to your .env file — "
            "see https://aistudio.google.com/apikey for a free key."
        )
    return genai.Client(api_key=api_key)


@tool
def draft_materials(posting_description: str, resume_summary: str) -> dict:
    """Draft tailored resume bullets and a cover letter for a posting.

    Args:
        posting_description: The job posting's description text.
        resume_summary: A summary of the candidate's resume/skills.

    Returns:
        dict with keys: tailored_bullets (list[str]), cover_letter (str).
    """
    client = _get_client()
    prompt = _DRAFT_PROMPT.format(
        resume_summary=resume_summary, posting_description=posting_description
    )
    response = client.models.generate_content(
        model=_MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_RESPONSE_SCHEMA,
        ),
    )
    parsed = json.loads(response.text)

    return {
        "tailored_bullets": parsed.get("tailored_bullets", []),
        "cover_letter": parsed.get("cover_letter", ""),
    }