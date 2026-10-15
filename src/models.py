from sqlalchemy import (
    Column, Integer, Text, Float, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Text, nullable=False)
    symbol = Column(Text, nullable=False)
    price = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)

    __table_args__ =(
        CheckConstraint("price IS NULL OR price >= 0", name="ck_price_nonneg"),
        CheckConstraint("volume IS NULL OR volume >= 0", name="ck_volume_nonneg"),
        UniqueConstraint("symbol", "timestamp", name="ux_market_data_symbol_timestamp"),
    )

class DataCheck(Base):
    __tablename__ = "data_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    check_name = Column(Text, nullable=False)
    passed = Column(Integer, nullable=False) # 0 for fail, 1 for pass
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    alerts = relationship("Alert", back_populates="check")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(Integer, ForeignKey("data_checks.id"), nullable=False)
    severity = Column(Text, nullable=False) #"warning" / "error"
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    check = relationship("DataCheck", back_populates="alerts")

