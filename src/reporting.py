from src.db_reports import get_latest_check_results, get_active_alerts 
from src.report_export import export_latest_checks_to_csv, export_active_alerts_to_csv
from src.logger import get_logger
from src.db import SessionLocal

logger = get_logger(__name__)

def generate_reports():
    with SessionLocal() as session:
        latest_checks = get_latest_check_results(session)
        active_alerts = get_active_alerts(session)
        logger.info("Latest Check Results:")

        for check in latest_checks:
            status = "PASS" if check.passed == 1 else "FAIL"
            logger.info(f"- [{check.id}] {check.check_name}: {status}")

        failed_checks = [check for check in latest_checks if check.passed == 0]

        if failed_checks:
            logger.info("Failed Check Details:")

            for check in failed_checks:
                logger.info(
                f"- check-id={check.id} | "
                f"{check.check_name} | "
                f"{check.message}"
                )

        logger.info("Active Alerts:")
        if active_alerts:
            for alert in active_alerts:
                logger.info(
                    f"- [alert {alert.id} -> check {alert.check_id}] "
                    f"{alert.severity.upper()} | {alert.check.check_name} | {alert.message}"
                )
        else:
            logger.info("- No active alerts.")

        latest_checks_csv = export_latest_checks_to_csv(latest_checks)
        active_alerts_csv = export_active_alerts_to_csv(active_alerts)

        logger.info(f"Exported latest checks to {latest_checks_csv}")
        logger.info(f"Exported active alerts to {active_alerts_csv}")
