# Job Application Agent

An autonomous agent, built with the [Strands Agents SDK](https://strandsagents.com), that runs the tedious parts of a job search in the background — and only interrupts you when there's a real decision to make.

## The problem

Job searching means re-checking job boards, re-reading postings, and re-tailoring your resume for each one — hours of repetitive work that mostly doesn't require judgment. The parts that DO require judgment (is this pay acceptable? is this a reasonable stretch role?) get buried under the parts that don't.

## Who it's for

Job seekers — especially early-career candidates applying to many roles — who want their search to run continuously without babysitting it.

## How it works

1. **Search** — polls job boards for new postings matching your target roles and locations.
2. **Score** — evaluates each posting's fit against your resume.
3. **Draft** — for strong fits, tailors resume bullets and a cover letter automatically.
4. **Review** — for borderline fits or unusual postings (pay below range, odd requirements), it flags the posting for YOUR decision instead of guessing.
5. **Track** — logs every action so nothing gets lost.

See the architecture diagram in the submission for the full flow.

## Setup

\`\`\`bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your model provider + Adzuna credentials
python src/agent.py
\`\`\`

## Status

Actively in development for the Amazon "Agents for Humans" hackathon. See commit history for progress.

## Optional: Amazon Bedrock AgentCore

This agent can be deployed on AgentCore for scheduled/autonomous runs instead of manual invocation.

## License

MIT — see `LICENSE`.