from typing import Iterable, Dict, Any
from sqlalchemy.orm import Session
from src.db import SessionLocal
from src.models import DataCheck, Alert
from src.logger import get_logger

logger = get_logger(__name__)

MAX_CHECK_HISTORY = 250

def clear_alerts_for_check_name(session: Session, check_name: str) -> None:
    """
    Remove any existing alerts linked to the given check_name.
    This keeps alerts as a 'current active issues only' table.
    """
    existing_alerts = (
        session.query(Alert)
        .join(DataCheck, Alert.check_id == DataCheck.id)
        .filter(DataCheck.check_name == check_name)
        .all()
    )

    for alert in existing_alerts:
        session.delete(alert)

def trim_data_check_history(session: Session, max_rows: int = MAX_CHECK_HISTORY) -> None:
    """
    Keep only the newest max_rows in data_checks.
    Older rows are deleted.
    """
    old_rows = (
        session.query(DataCheck)
        .order_by(DataCheck.id.desc())
        .offset(max_rows)
        .all()
    )

    for row in old_rows:
        #Delete any alert that still points to this old check row
        old_alerts = session.query(Alert).filter(Alert.check_id == row.id).all()
        for alert in old_alerts:
            session.delete(alert)

        session.delete(row)


def store_checks_and_alerts(session: Session, results: Iterable[Dict[str, Any]],
    max_history: int = MAX_CHECK_HISTORY) -> tuple[int, int]:
    """
    Store check results in data_checks and keep alerts as latest active issues only.
    
    Rules:
    - Every check result is stored in data_checks (history table)
    - Alerts keeps only the latest active alert per check_name.
    - If a check passes, old alerts for that check_name are removed.
    - If a check fails, old alerts for that check_name are replaced with the new one.
    - data_checks history is trimmed to max_history rows.

    Returns:
        (number_of_checks_inserted, number_of_alerts_created)
    """
    results = list(results)
    checks_inserted = 0
    alerts_created = 0 

    try:
        for result in results:
            check_row = DataCheck(
                check_name=result["check_name"],
                passed=1 if result["passed"] else 0,
                message=result["message"],
            )
            session.add(check_row)
            session.flush() # gives check_row.id
        
            checks_inserted += 1

            # Remove any older alert for this check type.
            clear_alerts_for_check_name(session, result["check_name"])

            # Only create a new alert if the latest check has failed.
            if not result["passed"]:
                alert_row = Alert(
                    check_id=check_row.id,
                    severity="warning",
                    message=result["message"],
                )
                session.add(alert_row)
                alerts_created += 1
            
        # Keep only the latest N history rows.
        trim_data_check_history(session, max_history)

        session.commit()
        return checks_inserted, alerts_created
    
    except Exception:
        session.rollback()
        raise



def save_check_results(check_results):
    with SessionLocal() as session:
        checks_inserted, alerts_created = store_checks_and_alerts(
            session,
            check_results
        )

        logger.info(
            f"Stored {checks_inserted} check results "
            f"and created {alerts_created} alerts."
        )