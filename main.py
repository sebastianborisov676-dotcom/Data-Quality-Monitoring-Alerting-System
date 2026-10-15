# Data Quality Monitoring & Alerting System

from src.logger import get_logger
from src.alerts import send_alert
from src.ingest import ingest_data
from src.checks import run_checks

from src.init_db import init_db
from src.db import SessionLocal
from src.db_ingest import upsert_market_data
from src.db_checks import store_checks_and_alerts
from src.db_reports import get_latest_check_results, get_active_alerts
from src.report_export import export_latest_checks_to_csv, export_active_alerts_to_csv

logger = get_logger(__name__)

def main() -> None:
    init_db()

    logger.info("App Started.")

    try:
        df = ingest_data("data/sample_market_data.csv")# df stands for DataFrame, a 2D labeled data structure with columns of potentially different types, similar to a spreadsheet or SQL table.
        logger.info(f"First 2 rows:\n{df.head(2)}")
    except Exception as e:
        send_alert(f"Ingestion Failed: {e}")
        logger.error(f"Ingestion failed: {e}")
        return
    
    rows = df[["timestamp", "symbol", "price", "volume"]].to_dict(orient="records") # Convert the DataFrame to a list of dictionaries where each dictionary represents a row.
    
    try:
        with SessionLocal() as session:
            upsert_market_data(session, rows)
    except Exception as e:
        send_alert(f"Database Ingestion has Failed: {e}")
        logger.error(f"Database ingestion has failed: {e}")
        return

    # Run checks and persist them
    check_results = run_checks(df)

    try:
        with SessionLocal() as session:
            checks_inserted, alerts_created = store_checks_and_alerts(session, check_results)
            logger.info(f"Stored {checks_inserted} check results and created {alerts_created} alerts.")
    except Exception as e:
        send_alert(f"Check persistence failed: {e}")
        logger.error(f"Check persistence failed: {e}")
        return
    
    try:
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
                for check in  failed_checks:
                    logger.info(f"- check-id={check.id} | {check.check_name} | {check.message}")

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
            
    except Exception as e:
        send_alert(f"Report query failed: {e}")
        logger.error(f"Report query failed: {e}")
        return
 
    for result in check_results:
        if not result["passed"]:
            send_alert(result["message"])

    logger.info("App Finished.")


if __name__ == "__main__":
    main()