from lix.analysis.indicators import is_bearish_rejection, is_bullish_rejection
from lix.domain.models import Direction, StrategyContext, TradeIdea
from lix.strategies.base import StrategyEngine


class KeyLevelRejectionEngine(StrategyEngine):
    name = "Daily Weekly Key Level Rejection"
    priority = 90

    async def evaluate(self, context: StrategyContext) -> TradeIdea | None:
        candles = context.candles
        if len(candles) < 96:
            return None

        latest = candles[-1]
        prior_day = candles[-96:-1]
        previous_high = max(candle.high for candle in prior_day)
        previous_low = min(candle.low for candle in prior_day)

        if latest.low < previous_low and latest.close > previous_low and is_bullish_rejection(latest):
            risk = max(latest.close - latest.low, 0.0001)
            entry = latest.close
            return TradeIdea(
                pair=context.pair,
                direction=Direction.BUY,
                strategy=self.name,
                confidence=74,
                entry=entry,
                stop_loss=entry - risk,
                take_profits=[entry + risk, entry + risk * 2, entry + risk * 3],
                risk_percent=0.5,
                explanation="Previous-day low sweep rejected with bullish rejection candle.",
            )

        if latest.high > previous_high and latest.close < previous_high and is_bearish_rejection(latest):
            risk = max(latest.high - latest.close, 0.0001)
            entry = latest.close
            return TradeIdea(
                pair=context.pair,
                direction=Direction.SELL,
                strategy=self.name,
                confidence=74,
                entry=entry,
                stop_loss=entry + risk,
                take_profits=[entry - risk, entry - risk * 2, entry - risk * 3],
                risk_percent=0.5,
                explanation="Previous-day high sweep rejected with bearish rejection candle.",
            )
        return None
