from pathlib import Path
import pandas as pd

from src.models import DataCheck, Alert

REPORTS_DIR = Path("reports")

def export_latest_checks_to_csv(latest_checks: list[DataCheck]) -> Path:
    """
    Export latest check results to reports/latest_checks.csv
    """
    REPORTS_DIR.mkdir(exist_ok=True)

    rows = []
    for check in latest_checks:
        rows.append(
            {
                "check_id": check.id,
                "check_name": check.check_name,
                "status": "PASS" if check.passed == 1 else "FAIL",
                "message": check.message,
                "created_at": check.created_at,
            }
        )

    df = pd.DataFrame(rows)
    output_path = REPORTS_DIR / "latest_checks.csv"
    df.to_csv(output_path, index=False)
    return output_path


def export_active_alerts_to_csv(active_alerts: list[Alert]) -> Path:
    """
    Export active alerts to reports/active_alerts.csv
    """
    REPORTS_DIR.mkdir(exist_ok=True)

    rows = []
    for alert in active_alerts:
        rows.append(
            {
                "alert_id": alert.id,
                "check.id": alert.check_id,
                "check_name": alert.check.check_name if alert.check else None,
                "severity": alert.severity,
                "message": alert.message,
                "created_at": alert.created_at,
            }
        )

    df = pd.DataFrame(rows)
    output_path = REPORTS_DIR / "active_alerts.csv"
    df.to_csv(output_path, index=False)
    return output_path