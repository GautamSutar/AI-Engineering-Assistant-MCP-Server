"""MCP server exposing job-ops tools over streamable HTTP.

Run directly: python -m app.mcp.server
"""

import os

from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from app.mcp.tools import github_ci, jobs

mcp = FastMCP("ai-ops-assistant", host="0.0.0.0", port=int(os.getenv("PORT", 8001)))


@mcp.tool()
def get_failed_jobs(hours: int = 24, limit: int = 20) -> list[dict]:
    """Get jobs that failed in the last N hours, most recent first."""
    return jobs.get_failed_jobs(hours=hours, limit=limit)


@mcp.tool()
def get_job_by_id(job_id: int) -> dict | None:
    """Get full details (including error message) for one job by its id."""
    return jobs.get_job_by_id(job_id)


@mcp.tool()
def search_jobs(query: str, limit: int = 20) -> list[dict]:
    """Search jobs by name, service, or error message substring."""
    return jobs.search_jobs(query, limit=limit)


@mcp.tool()
def get_job_stats() -> dict:
    """Get a quick count of jobs by status (total/failed/success/running)."""
    return jobs.get_job_stats()


@mcp.tool()
def get_recent_ci_failures(owner: str, repo: str, limit: int = 10) -> list[dict]:
    """Get real recent failed GitHub Actions runs for a repo (e.g. owner=GautamSutar)."""
    return github_ci.get_recent_ci_failures(owner, repo, limit=limit)


@mcp.tool()
def get_ci_failure_details(owner: str, repo: str, run_id: int) -> dict:
    """Get which job(s) and step(s) failed for a specific GitHub Actions run id."""
    return github_ci.get_ci_failure_details(owner, repo, run_id)


if __name__ == "__main__":
    import uvicorn

    app = mcp.streamable_http_app()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Mcp-Session-Id"],
    )
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8001)))
