from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from src.models import DataCheck, Alert


def get_latest_check_results(session: Session) -> list[DataCheck]:
    """
    Return the latest DataCheck row for each check_name.
    """
    latest_subquery = (
        session.query(
            DataCheck.check_name,
            func.max(DataCheck.id).label("latest_id"),
        )
        .group_by(DataCheck.check_name)
        .subquery()
    )

    latest_rows = (
        session.query(DataCheck)
        .join(latest_subquery, DataCheck.id == latest_subquery.c.latest_id)
        .order_by(DataCheck.id.desc())
        .all()
    )

    return latest_rows

def get_active_alerts(session: Session) -> list[Alert]:
    """
    Return all currently active alerts, newest first.
    """
    alerts = (
        session.query(Alert)
        .options(selectinload(Alert.check))
        .order_by(Alert.id.desc())
        .all()
    )

    return alerts