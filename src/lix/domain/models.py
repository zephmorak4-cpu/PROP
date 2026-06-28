from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Direction(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class MarketRegime(StrEnum):
    TRENDING = "trending"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    NEWS_DRIVEN = "news_driven"
    UNKNOWN = "unknown"


class TradeStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"


class TradeManagementAction(StrEnum):
    HOLD = "hold"
    MOVE_TO_BREAK_EVEN = "move_to_break_even"
    PARTIAL_PROFIT = "partial_profit"
    FULL_TAKE_PROFIT = "full_take_profit"
    EMERGENCY_EXIT = "emergency_exit"
    EXPIRE_TRADE = "expire_trade"


class Candle(BaseModel):
    pair: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


class StrategyContext(BaseModel):
    pair: str
    candles: list[Candle]
    regime: MarketRegime = MarketRegime.UNKNOWN
    metadata: dict[str, Any] = Field(default_factory=dict)


class TradeIdea(BaseModel):
    pair: str
    direction: Direction
    strategy: str
    confidence: int = Field(ge=0, le=100)
    entry: float
    stop_loss: float
    take_profits: list[float]
    risk_percent: float
    explanation: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ActiveTrade(BaseModel):
    pair: str
    direction: Direction
    strategy: str
    entry: float
    stop_loss: float
    take_profits: list[float]
    confidence: int = Field(ge=0, le=100)
    risk_percent: float
    status: TradeStatus = TradeStatus.ACTIVE
    reached_targets: list[int] = Field(default_factory=list)
    break_even_sent: bool = False
    emergency_exit_sent: bool = False
    opened_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_idea(cls, idea: TradeIdea) -> "ActiveTrade":
        return cls(
            pair=idea.pair,
            direction=idea.direction,
            strategy=idea.strategy,
            entry=idea.entry,
            stop_loss=idea.stop_loss,
            take_profits=idea.take_profits,
            confidence=idea.confidence,
            risk_percent=idea.risk_percent,
        )


class PairRank(BaseModel):
    pair: str
    score: int = Field(ge=0, le=100)
    reasons: list[str] = Field(default_factory=list)


class TradeUpdate(BaseModel):
    pair: str
    action: TradeManagementAction
    confidence: int = Field(ge=0, le=100)
    reason: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
