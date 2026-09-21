from datetime import datetime, timedelta

from sqlalchemy import or_

from app.db.database import SessionLocal
from app.db.models import Job


def get_failed_jobs(hours: int = 24, limit: int = 20) -> list[dict]:
    """Return failed jobs from the last `hours` hours, most recent first."""
    session = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        rows = (
            session.query(Job)
            .filter(Job.status == "failed", Job.started_at >= since)
            .order_by(Job.started_at.desc())
            .limit(limit)
            .all()
        )
        return [row.to_dict() for row in rows]
    finally:
        session.close()


def get_job_by_id(job_id: int) -> dict | None:
    """Return full details, including error message, for a single job by id."""
    session = SessionLocal()
    try:
        row = session.get(Job, job_id)
        return row.to_dict() if row else None
    finally:
        session.close()


def search_jobs(query: str, limit: int = 20) -> list[dict]:
    """Search jobs by name, service, or error message substring (case-insensitive)."""
    session = SessionLocal()
    try:
        like = f"%{query}%"
        rows = (
            session.query(Job)
            .filter(
                or_(
                    Job.name.ilike(like),
                    Job.service.ilike(like),
                    Job.error_message.ilike(like),
                )
            )
            .order_by(Job.started_at.desc())
            .limit(limit)
            .all()
        )
        return [row.to_dict() for row in rows]
    finally:
        session.close()


def get_job_stats() -> dict:
    """Return a quick count of jobs by status, useful for a health overview."""
    session = SessionLocal()
    try:
        rows = session.query(Job).all()
        stats = {"total": len(rows), "failed": 0, "success": 0, "running": 0}
        for row in rows:
            stats[row.status] = stats.get(row.status, 0) + 1
        return stats
    finally:
        session.close()
