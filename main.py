#Data Quality Monitoring & Alerting System

import pandas, sqlalchemy

from src.logger import get_logger
from src.alerts import send_alert
from src.ingest import ingest_data
from src.checks import run_checks

logger = get_logger(__name__)

def main() -> None:
    logger.info("App Started.")

    try:
        df = ingest_data("data/sample_market_data.csv")# df stands for DataFrame, a 2D labeled data structure with columns of potentially different types, similar to a spreadsheet or SQL table.
        logger.info(f"First 2 rows:\n{df.head(2)}")
    except Exception as e:
        send_alert(f"Ingestion Failed: {e}")
        logger.error(f"Ingestion failed: {e}")
        return
    
    check_results = run_checks(df)

    for result in check_results:
        if not result["passed"]:
            send_alert(result["message"])

    logger.info("App Finished.")


if __name__ == "__main__":
    main()