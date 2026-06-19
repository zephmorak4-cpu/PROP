from lix.domain.models import Direction, StrategyContext, TradeIdea
from lix.strategies.base import StrategyEngine


class LiquidityGrabEngine(StrategyEngine):
    name = "Liquidity Grab"
    priority = 75

    async def evaluate(self, context: StrategyContext) -> TradeIdea | None:
        candles = context.candles
        if len(candles) < 25:
            return None

        recent = candles[-20:-1]
        latest = candles[-1]
        highs = sorted(candle.high for candle in recent)
        lows = sorted(candle.low for candle in recent)
        equal_high_zone = sum(highs[-3:]) / 3
        equal_low_zone = sum(lows[:3]) / 3
        tolerance = max((max(highs) - min(lows)) * 0.03, 0.0001)

        if latest.high > equal_high_zone + tolerance and latest.close < equal_high_zone:
            risk = max(latest.high - latest.close, tolerance)
            entry = latest.close
            return TradeIdea(
                pair=context.pair,
                direction=Direction.SELL,
                strategy=self.name,
                confidence=73,
                entry=entry,
                stop_loss=entry + risk,
                take_profits=[entry - risk, entry - risk * 2, entry - risk * 3],
                risk_percent=0.5,
                explanation="Equal-high liquidity was taken and price closed back below the pool.",
            )

        if latest.low < equal_low_zone - tolerance and latest.close > equal_low_zone:
            risk = max(latest.close - latest.low, tolerance)
            entry = latest.close
            return TradeIdea(
                pair=context.pair,
                direction=Direction.BUY,
                strategy=self.name,
                confidence=73,
                entry=entry,
                stop_loss=entry - risk,
                take_profits=[entry + risk, entry + risk * 2, entry + risk * 3],
                risk_percent=0.5,
                explanation="Equal-low liquidity was taken and price closed back above the pool.",
            )
        return None
