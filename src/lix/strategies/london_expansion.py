from lix.analysis.indicators import average_true_range, body_size
from lix.domain.models import Direction, StrategyContext, TradeIdea
from lix.strategies.base import StrategyEngine


class LondonExpansionEngine(StrategyEngine):
    name = "London Expansion"
    priority = 80

    async def evaluate(self, context: StrategyContext) -> TradeIdea | None:
        candles = context.candles
        if len(candles) < 30:
            return None

        latest = candles[-1]
        atr = average_true_range(candles, period=14)
        if not atr:
            return None
        previous_range_high = max(candle.high for candle in candles[-12:-1])
        previous_range_low = min(candle.low for candle in candles[-12:-1])
        displacement = body_size(latest) > atr * 0.85

        if latest.close > previous_range_high and displacement:
            risk = max(latest.close - previous_range_low, atr)
            entry = latest.close
            return TradeIdea(
                pair=context.pair,
                direction=Direction.BUY,
                strategy=self.name,
                confidence=71,
                entry=entry,
                stop_loss=entry - risk,
                take_profits=[entry + risk, entry + risk * 1.8, entry + risk * 2.8],
                risk_percent=0.5,
                explanation="Momentum expansion broke above the recent range with displacement.",
            )

        if latest.close < previous_range_low and displacement:
            risk = max(previous_range_high - latest.close, atr)
            entry = latest.close
            return TradeIdea(
                pair=context.pair,
                direction=Direction.SELL,
                strategy=self.name,
                confidence=71,
                entry=entry,
                stop_loss=entry + risk,
                take_profits=[entry - risk, entry - risk * 1.8, entry - risk * 2.8],
                risk_percent=0.5,
                explanation="Momentum expansion broke below the recent range with displacement.",
            )
        return None
