# AI Engineering Assistant (MCP Server)

An AI ops assistant that answers questions about backend job failures by calling
real tools over MCP (Model Context Protocol). The LLM (via Groq) never guesses --
it calls MCP tools backed by a SQLite jobs table to get real data, then summarizes.

```
User -> FastAPI /chat -> LangGraph agent (Groq LLM) -> MCP tools -> SQLite
```

## Structure

```
app/
  db/       SQLAlchemy models + seed data (Job table)
  mcp/      MCP server exposing job-ops tools (get_failed_jobs, search_jobs, ...)
  agent/    LangGraph ReAct agent wired to Groq + MCP tools
  api/      FastAPI routes (/chat, /health)
main.py     FastAPI entrypoint
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

copy .env.example .env
# edit .env and set GROQ_API_KEY

python -m app.db.seed           # creates + seeds app/db/ops.db
```

## Run (two processes)

Terminal 1 -- MCP server (tools + SQLite):

```bash
python -m app.mcp.server
```

Terminal 2 -- FastAPI app (agent + chat endpoint):

```bash
uvicorn main:app --reload --port 8000
```

## Try it

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What jobs failed recently and why?\"}"
```

The agent will call `get_failed_jobs` (and possibly `get_job_by_id` /
`search_jobs`) via MCP, then summarize the real failures from SQLite.

## Real data: GitHub Actions CI failures

`get_failed_jobs` etc. only ever see seeded, fake data. For real data, two more
tools (`app/mcp/tools/github_ci.py`) query the live GitHub Actions API for any
repo you have access to:

- `get_recent_ci_failures(owner, repo, limit=10)` -- real failed workflow runs
- `get_ci_failure_details(owner, repo, run_id)` -- which job/step failed

Requires a GitHub fine-grained PAT with **Actions: read** permission, set as
`GITHUB_PERSONAL_ACCESS_TOKEN` in `.env`. This repo's own `.github/workflows/ci.yml`
gives you something real to query immediately:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Are there any recent failed CI runs on GautamSutar/AI-Engineering-Assistant-MCP-Server?\"}"
```

## Roadmap

- [ ] Tool permission tiers (read / write / dangerous) with human-in-the-loop approval
- [ ] Docker / monitoring tool servers
- [ ] Auth (API key or JWT) on the FastAPI layer
- [ ] Streaming responses
- [ ] Docker Compose for MCP server + API + Postgres
