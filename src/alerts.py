from src.logger import get_logger

logger = get_logger(__name__)

def send_alert(message: str) -> None:
    logger.warning(f"ALERT: {message}")

def notify_failed_checks(check_results):
    for result in check_results:
        if not result["passed"]:
            send_alert(result["message"])