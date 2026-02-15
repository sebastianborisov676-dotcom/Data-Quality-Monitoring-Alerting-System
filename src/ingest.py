from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.logger import get_logger

logger = get_logger(__name__)

REQUIRED_COLUMNS = {"timestamp","symbol","price","volume"}



def ingest_data(csv_path: str | Path) -> pd.DataFrame:
    """
    Load market data from a CSV file and validate basic structure.
    """
    
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    
    logger.info(f"Loading data from {path}")

    df = pd.read_csv(path)

    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"CSV is missing required columns: {sorted(missing_cols)}")
    
    logger.info(f"Loaded {len(df)} rows with columns: {list(df.columns)}")
    return df