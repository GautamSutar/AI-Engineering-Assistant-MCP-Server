"""MCP server exposing job-ops tools over streamable HTTP.

Run directly: python -m app.mcp.server
"""

from mcp.server.fastmcp import FastMCP

from app.mcp.tools import jobs

mcp = FastMCP("ai-ops-assistant", host="0.0.0.0", port=8001)


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


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
