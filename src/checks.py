from typing import List, Dict

import pandas as pd

from src.logger import get_logger

logger = get_logger(__name__)

def check_missing_values(
    df: pd.DataFrame,
    column: str,
) -> Dict[str, object]:
    """
    Check whether a column contains missing values.
    """
    missing_count = int(df[column].isna().sum())

    if missing_count > 0:
        logger.info(f"Missing values detected in column '{column}': {missing_count}")

        return {
            "check_name": f"missing_values_{column}",
            "passed": False,
            "message": f"{missing_count} rows have missing values in '{column}'"
        }
    
    return {
        "check_name": f"missing_values_{column}",
        "passed": True,
        "message": "No missing values detected."
    }

def check_value_range(
        df: pd.DataFrame,
        column: str,
        min_value: float,
        max_value: float
) -> Dict[str, object]:
    """
    Check whether values in column fall within an expected range.
    """
    s = df[column]

    non_missing = s.dropna()#This only evaluates range of non-missing values.

    invalid_mask = (non_missing < min_value) | (non_missing > max_value)
    invalid_count = int(invalid_mask.sum())

    if invalid_count > 0:
        
        bad_examples = non_missing[invalid_mask].head(3).tolist()

        return {
            "check_name": f"value_range_{column}",
            "passed": False,
            "message": (
                f"{invalid_count} non-missing values in '{column}' "
                f"are outside of the expected range [{min_value}, {max_value}]. Examples: {bad_examples}"
            ),
        }

    return {
        "check_name": f"value_range_{column}",
        "passed": True,
        "message": f"All non-missing values in '{column}' are within the [{min_value}, {max_value}] range.",
    }

def check_non_negative(df: pd.DataFrame, column: str) -> Dict[str, object]:
    """
    Check whether values in column are non-negative.
    """
    s = df[column].dropna()
    invalid_mask = s < 0
    invalid_count = int(invalid_mask.sum())

    if invalid_count > 0:
        bad_examples = s[invalid_mask].head(3).tolist()
        return {
            "check_name": f"non_negative_{column}",
            "passed": False,
            "message":
                f"{invalid_count} values in '{column}' are negative. Examples: {bad_examples}",
        }

    return {
        "check_name": f"non_negative_{column}",
        "passed": True,
        "message": f"No negative values found in '{column}'",
    }

def run_checks(df: pd.DataFrame) -> List[Dict[str, object]]:
    """
    Run all data quality checks and returns their results.
    """
    logger.info("Running data quality checks")

    results: List[Dict[str, object]] = []

    results.append(check_missing_values(df,"price"))
    results.append(check_value_range(df, "price", min_value=0, max_value=1000))
    results.append(check_non_negative(df, "volume"))

    return results