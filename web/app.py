"""
FastAPI web frontend for the Job Application Agent.

Serves a small dashboard showing agent activity and the review queue,
and exposes endpoints to trigger a run and check pending decisions.
This is the publicly deployed "live demo" for judges — separate from
the Bedrock AgentCore Runtime entrypoint (src/agentcore_app.py), which
satisfies the hackathon's AgentCore-deployment scoring criterion via
the AWS-authenticated invoke path.

Run locally:
    pip install fastapi "uvicorn[standard]"
    uvicorn web.app:app --reload --port 8080
"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import run_once  # noqa: E402
from tools.tracker import get_pending_reviews  # noqa: E402

app = FastAPI(title="Job Application Agent")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class RunRequest(BaseModel):
    resume_summary: str
    target_roles: list[str]
    locations: list[str]


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/run")
def run_agent(req: RunRequest):
    result = run_once(req.model_dump())
    return {"result": result}


@app.get("/api/reviews")
def reviews():
    return {"pending": get_pending_reviews()}


@app.get("/api/health")
def health():
    return {"status": "ok"}