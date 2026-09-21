"""Creates the SQLite schema and seeds a handful of realistic job records.

Run directly: python -m app.db.seed
"""

from datetime import datetime, timedelta

from app.db.database import Base, SessionLocal, engine
from app.db.models import Job

SEED_JOBS = [
    dict(
        name="sync-orders",
        service="order-service",
        status="failed",
        error_message="connection pool exhausted: active=100 max=100",
        started_offset_min=12,
        duration_min=2,
    ),
    dict(
        name="send-invoice-emails",
        service="notification-service",
        status="failed",
        error_message="SMTP timeout after 30s connecting to smtp.provider.com",
        started_offset_min=45,
        duration_min=1,
    ),
    dict(
        name="reconcile-payments",
        service="payment-service",
        status="failed",
        error_message="ValueError: currency mismatch USD != INR for txn_8842",
        started_offset_min=90,
        duration_min=3,
    ),
    dict(
        name="refresh-analytics-cache",
        service="analytics-service",
        status="success",
        error_message=None,
        started_offset_min=20,
        duration_min=5,
    ),
    dict(
        name="cleanup-expired-sessions",
        service="auth-service",
        status="success",
        error_message=None,
        started_offset_min=200,
        duration_min=1,
    ),
    dict(
        name="generate-weekly-report",
        service="reporting-service",
        status="running",
        error_message=None,
        started_offset_min=2,
        duration_min=None,
    ),
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if session.query(Job).count() > 0:
            print("Jobs table already seeded, skipping.")
            return

        now = datetime.utcnow()
        for item in SEED_JOBS:
            started_at = now - timedelta(minutes=item["started_offset_min"])
            finished_at = (
                started_at + timedelta(minutes=item["duration_min"])
                if item["duration_min"] is not None
                else None
            )
            session.add(
                Job(
                    name=item["name"],
                    service=item["service"],
                    status=item["status"],
                    error_message=item["error_message"],
                    started_at=started_at,
                    finished_at=finished_at,
                )
            )
        session.commit()
        print(f"Seeded {len(SEED_JOBS)} jobs into {engine.url}")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
