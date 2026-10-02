"""Real-data tool: queries live GitHub Actions CI runs via GitHub's REST API.

Unlike app/mcp/tools/jobs.py (seeded SQLite data), this hits the real GitHub
API for whichever owner/repo the caller asks about, using a GitHub personal
access token for auth.
"""

import os

import httpx

GITHUB_API = "https://api.github.com"


def _headers() -> dict:
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_PERSONAL_ACCESS_TOKEN is not set -- generate a fine-grained "
            "PAT with 'Actions: read' permission and add it to your .env"
        )
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ai-ops-assistant-mcp-server",
    }


def get_recent_ci_failures(owner: str, repo: str, limit: int = 10) -> list[dict]:
    """Get the most recent failed GitHub Actions workflow runs for owner/repo."""
    resp = httpx.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/actions/runs",
        headers=_headers(),
        params={"status": "failure", "per_page": limit},
        timeout=20,
    )
    resp.raise_for_status()
    runs = resp.json().get("workflow_runs", [])
    return [
        {
            "run_id": run["id"],
            "workflow_name": run["name"],
            "branch": run["head_branch"],
            "event": run["event"],
            "actor": run["actor"]["login"] if run.get("actor") else None,
            "created_at": run["created_at"],
            "html_url": run["html_url"],
        }
        for run in runs
    ]


def get_ci_failure_details(owner: str, repo: str, run_id: int) -> dict:
    """Get which job(s) and step(s) failed for a specific GitHub Actions run."""
    resp = httpx.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
        headers=_headers(),
        timeout=20,
    )
    resp.raise_for_status()
    jobs = resp.json().get("jobs", [])

    failed_jobs = []
    for job in jobs:
        if job["conclusion"] != "failure":
            continue
        failed_steps = [
            step["name"] for step in job.get("steps", []) if step["conclusion"] == "failure"
        ]
        failed_jobs.append(
            {
                "job_name": job["name"],
                "failed_steps": failed_steps,
                "html_url": job["html_url"],
            }
        )

    return {"run_id": run_id, "failed_jobs": failed_jobs}
