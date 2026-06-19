from lix.domain.models import Candle


def average_true_range(candles: list[Candle], period: int = 14) -> float | None:
    if len(candles) < period + 1:
        return None
    true_ranges: list[float] = []
    for current, previous in zip(candles[-period:], candles[-period - 1 : -1], strict=False):
        true_ranges.append(
            max(
                current.high - current.low,
                abs(current.high - previous.close),
                abs(current.low - previous.close),
            )
        )
    return sum(true_ranges) / len(true_ranges) if true_ranges else None


def body_size(candle: Candle) -> float:
    return abs(candle.close - candle.open)


def candle_range(candle: Candle) -> float:
    return candle.high - candle.low


def is_bullish_rejection(candle: Candle) -> bool:
    lower_wick = min(candle.open, candle.close) - candle.low
    upper_wick = candle.high - max(candle.open, candle.close)
    return candle.close > candle.open and lower_wick > upper_wick * 1.5


def is_bearish_rejection(candle: Candle) -> bool:
    upper_wick = candle.high - max(candle.open, candle.close)
    lower_wick = min(candle.open, candle.close) - candle.low
    return candle.close < candle.open and upper_wick > lower_wick * 1.5
