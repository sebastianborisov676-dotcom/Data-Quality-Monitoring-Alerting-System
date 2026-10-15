from typing import Iterable, Dict, Any
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session
from src.models import MarketData

def upsert_market_data(session: Session, rows: Iterable[Dict[str, Any]]) -> int:
    """
    Upsert rows into market_data using UNIQUE(symbol, timestamp).
    Returns number of input rows processed.
    """
    rows = list(rows)
    if not rows:
        return 0

    stmt = insert(MarketData).values(rows)

    # "excluded" in SQLAlchemy becomes stmt.excluded.<col>
    stmt = stmt.on_conflict_do_update(
        index_elements=["symbol", "timestamp"],
        set_={
            "price": stmt.excluded.price,
            "volume": stmt.excluded.volume,
        },          
    )

    try:
        session.execute(stmt)
        session.commit()
    except Exception:
        session.rollback()
        raise
    
    return len(rows)
