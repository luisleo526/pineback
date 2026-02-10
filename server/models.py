"""
SQLAlchemy ORM models for the backtests table.
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Date, DateTime, Integer, Numeric, CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .db import Base


def utcnow():
    return datetime.now(timezone.utc)


class Backtest(Base):
    __tablename__ = "backtests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    strategy_name = Column(String, nullable=False)
    pinescript = Column(Text, nullable=False)
    symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    initial_capital = Column(Numeric(20, 2), nullable=False, default=10000)
    params = Column(JSONB, nullable=False, default=dict)
    mode = Column(String, nullable=False, default="magnifier")

    # Lifecycle
    status = Column(String, nullable=False, default="pending")
    progress = Column(Integer, nullable=False, default=0)
    progress_message = Column(String, nullable=False, default="")
    error_message = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Denormalized summary stats
    total_return = Column(Numeric(12, 4), nullable=True)
    sharpe_ratio = Column(Numeric(8, 4), nullable=True)
    max_drawdown = Column(Numeric(8, 4), nullable=True)
    win_rate = Column(Numeric(8, 4), nullable=True)
    total_trades = Column(Integer, nullable=True)
    profit_factor = Column(Numeric(8, 4), nullable=True)
    final_value = Column(Numeric(20, 2), nullable=True)

    # Full result payload
    result_json = Column(JSONB, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','running','completed','failed')",
            name="valid_status",
        ),
        CheckConstraint(
            "mode IN ('standard','magnifier')",
            name="valid_mode",
        ),
        Index("idx_backtests_submitted", "submitted_at"),
    )

    def to_summary_dict(self):
        """Return summary fields (no result_json) for list endpoints."""
        return {
            "id": str(self.id),
            "strategy_name": self.strategy_name,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "timeframe": self.timeframe,
            "mode": self.mode,
            "status": self.status,
            "progress": self.progress,
            "progress_message": self.progress_message,
            "error_message": self.error_message,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_return": float(self.total_return) if self.total_return is not None else None,
            "sharpe_ratio": float(self.sharpe_ratio) if self.sharpe_ratio is not None else None,
            "max_drawdown": float(self.max_drawdown) if self.max_drawdown is not None else None,
            "win_rate": float(self.win_rate) if self.win_rate is not None else None,
            "total_trades": self.total_trades,
            "profit_factor": float(self.profit_factor) if self.profit_factor is not None else None,
            "final_value": float(self.final_value) if self.final_value is not None else None,
        }

    def to_detail_dict(self):
        """Return full detail including result_json (for single-item GET)."""
        d = self.to_summary_dict()
        if self.status == "completed" and self.result_json:
            d["result_json"] = self.result_json
        return d
