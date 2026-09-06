"""Tool: search_postings

Pulls new job postings matching the candidate's target roles/locations,
using the Adzuna Jobs API (https://developer.adzuna.com/). Free tier,
structured JSON, no scraping fragility — good for a hackathon demo a judge
will re-run.

Requires ADZUNA_APP_ID and ADZUNA_APP_KEY in your environment (see
.env.example). Sign up free at https://developer.adzuna.com/.

Adzuna is country-scoped (one country code per call, e.g. "us", "gb", "in").
There's no dedicated Nepal endpoint at time of writing — if your target
locations aren't covered, default to "us" + "Remote" filtering, or swap
in a different source using the same tool signature.

A local `seen_ids.json` file tracks postings already returned, so repeated
runs only surface NEW postings to the rest of the pipeline.
"""

import json
import os
from pathlib import Path

import requests
from strands import tool

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"
SEEN_IDS_PATH = Path(__file__).parent.parent / "data" / "seen_ids.json"


def _load_seen_ids() -> set[str]:
    if not SEEN_IDS_PATH.exists():
        return set()
    return set(json.loads(SEEN_IDS_PATH.read_text()))


def _save_seen_ids(seen: set[str]) -> None:
    SEEN_IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEEN_IDS_PATH.write_text(json.dumps(sorted(seen)))


@tool
def search_postings(
    target_roles: list[str], locations: list[str], country: str = "us"
) -> list[dict]:
    """Search job boards for new postings matching the given roles and locations.

    Args:
        target_roles: Job titles/categories to search for, e.g. ["Data Scientist"].
        locations: Free-text location filters, e.g. ["Remote", "New York"].
            Applied as a substring filter on Adzuna's returned location field.
        country: Adzuna country code, e.g. "us", "gb", "in". Defaults to "us".

    Returns:
        A list of NEW postings only (already-seen ones are filtered out),
        each a dict with keys: id, title, company, location, url,
        description, salary_range.
    """
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise RuntimeError(
            "Missing ADZUNA_APP_ID / ADZUNA_APP_KEY. Sign up free at "
            "https://developer.adzuna.com/ and add them to your .env file."
        )

    seen_ids = _load_seen_ids()
    results: list[dict] = []

    for role in target_roles:
        resp = requests.get(
            f"{ADZUNA_BASE_URL}/{country}/search/1",
            params={
                "app_id": app_id,
                "app_key": app_key,
                "what": role,
                "results_per_page": 20,
                "content-type": "application/json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        for job in resp.json().get("results", []):
            job_id = str(job.get("id"))
            if job_id in seen_ids:
                continue
            location_display = job.get("location", {}).get("display_name", "")
            if locations and not any(
                loc.lower() in location_display.lower()
                or loc.lower() == "remote"
                for loc in locations
            ):
                continue
            results.append(
                {
                    "id": job_id,
                    "title": job.get("title", ""),
                    "company": job.get("company", {}).get("display_name", ""),
                    "location": location_display,
                    "url": job.get("redirect_url", ""),
                    "description": job.get("description", ""),
                    "salary_range": (
                        f"{job.get('salary_min', '?')}-{job.get('salary_max', '?')}"
                        if job.get("salary_min")
                        else "Not listed"
                    ),
                }
            )
            seen_ids.add(job_id)

    _save_seen_ids(seen_ids)
    return results