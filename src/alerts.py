from src.logger import get_logger

logger = get_logger(__name__)

def send_alert(message: str) -> None:
    logger.warning(f"ALERT: {message}")