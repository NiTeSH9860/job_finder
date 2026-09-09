# Job Application Agent

An autonomous agent, built with the [Strands Agents SDK](https://strandsagents.com), that runs the tedious parts of a job search in the background — and only interrupts you when there's a real decision to make.

Built for the Amazon "Agents for Humans" hackathon, Professional Agents track.

## The problem

Job searching means re-checking job boards, re-reading postings, and re-tailoring your resume for each one — hours of repetitive work that mostly doesn't require judgment. The parts that DO require judgment (is this pay acceptable? is this a reasonable stretch role?) get buried under the parts that don't.

## Who it's for

Job seekers — especially early-career candidates applying to many roles — who want their search to run continuously without babysitting it.

## How it works

1. **Search** (`job_search.py`) — polls the Adzuna Jobs API for new postings matching your target roles and locations. Tracks seen postings locally so re-runs only surface genuinely new ones.
2. **Score** (`fit_scorer.py`) — evaluates each posting's fit against your resume using Sentence-BERT embeddings + cosine similarity.
3. **Draft** (`drafter.py`) — for strong fits, calls Gemini to tailor resume bullets and a cover letter.
4. **Review** (`tracker.py` — `needs_human_review`) — for borderline fits or unusual postings (pay below range, odd requirements), flags the posting for YOUR decision instead of guessing. This is what makes it an *agent* rather than a pipeline: the model decides mid-run when to hand control back.
5. **Track** (`tracker.py` — `log_application`) — logs every action to a local SQLite database so nothing gets lost.

See `architecture.svg` for the full flow diagram.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # fill in your model provider + Adzuna credentials
python src/agent.py
```

Get free API credentials:
- Adzuna: https://developer.adzuna.com/
- Gemini: https://aistudio.google.com/apikey

## Testing

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

15 tests covering the tracker's SQLite persistence and the fit-scorer's similarity/threshold logic.

## Project structure
src/
agent.py # Strands orchestrator, system prompt, tool wiring
tools/
job_search.py # Adzuna API integration
fit_scorer.py # Embedding-based fit scoring
drafter.py # Gemini-based resume/cover letter drafting
tracker.py # SQLite logging + human-review queue
tests/ # pytest suite
architecture.svg # architecture diagram


## Optional: Amazon Bedrock AgentCore

This agent can be deployed on AgentCore for scheduled/autonomous runs instead of manual invocation.

## License

MIT — see `LICENSE`.