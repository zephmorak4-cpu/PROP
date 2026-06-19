from lix.domain.models import Candle, MarketRegime


class MarketRegimeEngine:
    def classify(self, candles: list[Candle], news_driven: bool = False) -> MarketRegime:
        if news_driven:
            return MarketRegime.NEWS_DRIVEN
        if len(candles) < 30:
            return MarketRegime.UNKNOWN

        ranges = [candle.high - candle.low for candle in candles[-30:]]
        avg_range = sum(ranges) / len(ranges)
        recent_range = sum(ranges[-5:]) / 5

        if recent_range > avg_range * 1.8:
            return MarketRegime.HIGH_VOLATILITY
        if recent_range < avg_range * 0.55:
            return MarketRegime.LOW_VOLATILITY

        net_move = abs(candles[-1].close - candles[-30].close)
        total_range = sum(ranges)
        if total_range and net_move / total_range > 0.35:
            return MarketRegime.TRENDING
        return MarketRegime.RANGING
