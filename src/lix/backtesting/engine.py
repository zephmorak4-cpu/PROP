from dataclasses import dataclass
from datetime import datetime

from lix.config import Settings
from lix.domain.models import Candle, TradeIdea
from lix.strategies.asian_liquidity_sweep import AsianLiquiditySweepEngine


@dataclass(frozen=True)
class BacktestResult:
    pair: str
    started_at: datetime | None
    ended_at: datetime | None
    total_setups: int
    average_confidence: float
    average_stop_size: float
    average_tp1_size: float
    ideas: list[TradeIdea]


class AsianSweepBacktester:
    def __init__(self, settings: Settings):
        self.strategy = AsianLiquiditySweepEngine(settings)

    async def run(self, pair: str, candles: list[Candle], window: int = 200) -> BacktestResult:
        ideas: list[TradeIdea] = []
        for index in range(window, len(candles) + 1):
            sample = candles[index - window : index]
            idea = await self.strategy.evaluate(
                context=self._context(pair, sample),
            )
            if idea:
                ideas.append(idea)

        return BacktestResult(
            pair=pair,
            started_at=candles[0].timestamp if candles else None,
            ended_at=candles[-1].timestamp if candles else None,
            total_setups=len(ideas),
            average_confidence=self._average([idea.confidence for idea in ideas]),
            average_stop_size=self._average([abs(idea.entry - idea.stop_loss) for idea in ideas]),
            average_tp1_size=self._average([abs(idea.take_profits[0] - idea.entry) for idea in ideas]),
            ideas=ideas,
        )

    def _context(self, pair: str, candles: list[Candle]):
        from lix.domain.models import StrategyContext

        return StrategyContext(pair=pair, candles=candles)

    def _average(self, values: list[float]) -> float:
        return sum(values) / len(values) if values else 0
