from lix.analysis.indicators import average_true_range
from lix.domain.models import Direction, StrategyContext, TradeIdea
from lix.strategies.base import StrategyEngine


class VolatilityExpansionEngine(StrategyEngine):
    name = "Volatility Compression Expansion"
    priority = 60

    async def evaluate(self, context: StrategyContext) -> TradeIdea | None:
        candles = context.candles
        if len(candles) < 50:
            return None

        current_atr = average_true_range(candles, period=14)
        previous_atr = average_true_range(candles[-35:-14], period=14)
        if not current_atr or not previous_atr:
            return None
        compressed = previous_atr < current_atr * 0.75
        latest = candles[-1]
        compression_high = max(candle.high for candle in candles[-20:-1])
        compression_low = min(candle.low for candle in candles[-20:-1])

        if compressed and latest.close > compression_high:
            risk = max(latest.close - compression_low, current_atr)
            entry = latest.close
            return TradeIdea(
                pair=context.pair,
                direction=Direction.BUY,
                strategy=self.name,
                confidence=70,
                entry=entry,
                stop_loss=entry - risk,
                take_profits=[entry + risk, entry + risk * 1.7, entry + risk * 2.5],
                risk_percent=0.4,
                explanation="Volatility expanded after compression and broke above the range.",
            )

        if compressed and latest.close < compression_low:
            risk = max(compression_high - latest.close, current_atr)
            entry = latest.close
            return TradeIdea(
                pair=context.pair,
                direction=Direction.SELL,
                strategy=self.name,
                confidence=70,
                entry=entry,
                stop_loss=entry + risk,
                take_profits=[entry - risk, entry - risk * 1.7, entry - risk * 2.5],
                risk_percent=0.4,
                explanation="Volatility expanded after compression and broke below the range.",
            )
        return None
