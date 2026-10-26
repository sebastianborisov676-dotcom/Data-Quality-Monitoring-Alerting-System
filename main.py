# Data Quality Monitoring & Alerting System

from src.logger import get_logger
from src.alerts import send_alert, notify_failed_checks
from src.ingest import ingest_data
from src.checks import run_checks

from src.init_db import init_db
from src.db_ingest import save_market_data
from src.db_checks import save_check_results
from src.reporting import generate_reports

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
        save_market_data(rows)
    except Exception as e:
        send_alert(f"Database Ingestion has Failed: {e}")
        logger.error(f"Database ingestion has failed: {e}")
        return

    # Run checks and persist them
    check_results = run_checks(df)

    try:
        save_check_results(check_results)
    except Exception as e:
        send_alert(f"Check persistence failed: {e}")
        logger.error(f"Check persistence failed: {e}")
        return

    try:
        generate_reports()
    except Exception as e:
        send_alert(f"Report generation failed: {e}")
        logger.error(f"Report generation failed: {e}")
        return
 
    notify_failed_checks(check_results)

    logger.info("App Finished.")


if __name__ == "__main__":
    main()