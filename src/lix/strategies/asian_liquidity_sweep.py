from lix.domain.models import Direction, StrategyContext, TradeIdea
from lix.strategies.base import StrategyEngine


class AsianLiquiditySweepEngine(StrategyEngine):
    name = "Asian Liquidity Sweep"
    priority = 100

    async def evaluate(self, context: StrategyContext) -> TradeIdea | None:
        candles = context.candles
        if len(candles) < 40:
            return None

        asian_window = candles[-40:-16]
        recent = candles[-8:]
        asian_high = max(candle.high for candle in asian_window)
        asian_low = min(candle.low for candle in asian_window)
        latest = candles[-1]

        swept_high = any(candle.high > asian_high for candle in recent)
        swept_low = any(candle.low < asian_low for candle in recent)

        if swept_low and latest.close > asian_low:
            risk = max(latest.close - min(candle.low for candle in recent), 0.0001)
            entry = latest.close
            return TradeIdea(
                pair=context.pair,
                direction=Direction.BUY,
                strategy=self.name,
                confidence=72,
                entry=entry,
                stop_loss=entry - risk,
                take_profits=[entry + risk, entry + risk * 2, entry + risk * 3],
                risk_percent=0.5,
                explanation="Asian low sweep with rejection back inside the range.",
            )

        if swept_high and latest.close < asian_high:
            risk = max(max(candle.high for candle in recent) - latest.close, 0.0001)
            entry = latest.close
            return TradeIdea(
                pair=context.pair,
                direction=Direction.SELL,
                strategy=self.name,
                confidence=72,
                entry=entry,
                stop_loss=entry + risk,
                take_profits=[entry - risk, entry - risk * 2, entry - risk * 3],
                risk_percent=0.5,
                explanation="Asian high sweep with rejection back inside the range.",
            )
        return None
