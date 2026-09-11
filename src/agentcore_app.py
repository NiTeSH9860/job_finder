"""
AgentCore Runtime entrypoint for the Job Application Agent.

Wraps agent.run_once() as an HTTP service using the Bedrock AgentCore
Runtime Python SDK, so judges (and the Devpost "live demo" link) can
invoke the agent without running it locally.

Local test:
    pip install bedrock-agentcore
    python src/agentcore_app.py
    curl -X POST http://localhost:8080/invocations \
      -H "Content-Type: application/json" \
      -d '{"resume_summary": "Entry-level data scientist, Python, scikit-learn", "target_roles": ["Data Scientist"], "locations": ["Remote"]}'

Deploy (see README's Deployment section):
    npm install -g @aws/agentcore
    agentcore create
    agentcore deploy
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from agent import run_once

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict) -> dict:
    """AgentCore entrypoint. Expects a candidate profile in the request payload."""
    candidate_profile = {
        "resume_summary": payload.get("resume_summary", ""),
        "target_roles": payload.get("target_roles", []),
        "locations": payload.get("locations", []),
    }
    if not candidate_profile["resume_summary"]:
        return {"error": "Missing 'resume_summary' in request payload."}

    result = run_once(candidate_profile)
    return {"result": result}


if __name__ == "__main__":
    app.run()