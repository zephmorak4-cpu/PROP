from dataclasses import dataclass
from datetime import UTC, datetime, time

from lix.analysis.indicators import (
    average_true_range,
    body_size,
    candle_range,
    is_bearish_rejection,
    is_bullish_rejection,
)
from lix.config import Settings
from lix.domain.models import Candle, Direction, StrategyContext, TradeIdea
from lix.strategies.base import StrategyEngine


@dataclass(frozen=True)
class AsianSessionRange:
    high: float
    low: float
    started_at: datetime
    ended_at: datetime


class AsianLiquiditySweepEngine(StrategyEngine):
    name = "Asian Liquidity Sweep"
    priority = 100

    def __init__(self, settings: Settings):
        self.settings = settings

    async def evaluate(self, context: StrategyContext) -> TradeIdea | None:
        candles = context.candles
        if len(candles) < self.settings.atr_period + 20:
            return None

        latest = candles[-1]
        if not self._is_london_session(latest.timestamp):
            return None

        asian_range = self._asian_range(candles, latest.timestamp)
        if not asian_range:
            return None

        atr = average_true_range(candles, self.settings.atr_period)
        if not atr or atr < self.settings.min_atr_pips * self._pip_size(context.pair):
            return None

        london_candles = [
            candle
            for candle in candles
            if asian_range.ended_at <= candle.timestamp <= latest.timestamp
        ]
        if len(london_candles) < 4:
            return None

        sweep_buffer = atr * self.settings.sweep_buffer_atr_multiplier
        stop_buffer = atr * self.settings.stop_buffer_atr_multiplier

        buy_sweep = self._find_low_sweep(london_candles, asian_range.low, sweep_buffer)
        if buy_sweep and self._buy_confirmed(london_candles, buy_sweep, asian_range, atr):
            return self._build_buy(context.pair, london_candles, buy_sweep, asian_range, stop_buffer)

        sell_sweep = self._find_high_sweep(london_candles, asian_range.high, sweep_buffer)
        if sell_sweep and self._sell_confirmed(london_candles, sell_sweep, asian_range, atr):
            return self._build_sell(context.pair, london_candles, sell_sweep, asian_range, stop_buffer)

        return None

    def _asian_range(
        self,
        candles: list[Candle],
        reference: datetime,
    ) -> AsianSessionRange | None:
        reference = reference.astimezone(UTC)
        start = datetime.combine(
            reference.date(),
            time(self.settings.asian_session_start_hour_utc, tzinfo=UTC),
        )
        end = datetime.combine(
            reference.date(),
            time(self.settings.asian_session_end_hour_utc, tzinfo=UTC),
        )
        session_candles = [candle for candle in candles if start <= candle.timestamp < end]
        if len(session_candles) < 4:
            return None
        return AsianSessionRange(
            high=max(candle.high for candle in session_candles),
            low=min(candle.low for candle in session_candles),
            started_at=start,
            ended_at=end,
        )

    def _is_london_session(self, timestamp: datetime) -> bool:
        timestamp = timestamp.astimezone(UTC)
        return self.settings.london_session_start_hour_utc <= timestamp.hour < (
            self.settings.london_session_end_hour_utc
        )

    def _find_low_sweep(
        self,
        candles: list[Candle],
        asian_low: float,
        buffer: float,
    ) -> Candle | None:
        swept = [candle for candle in candles if candle.low < asian_low - buffer]
        return swept[-1] if swept else None

    def _find_high_sweep(
        self,
        candles: list[Candle],
        asian_high: float,
        buffer: float,
    ) -> Candle | None:
        swept = [candle for candle in candles if candle.high > asian_high + buffer]
        return swept[-1] if swept else None

    def _buy_confirmed(
        self,
        london_candles: list[Candle],
        sweep: Candle,
        asian_range: AsianSessionRange,
        atr: float,
    ) -> bool:
        after_sweep = self._candles_after_sweep(london_candles, sweep)
        if not after_sweep:
            return False
        latest = london_candles[-1]
        if latest.close <= asian_range.low:
            return False
        if not self._bullish_confirmation(after_sweep[-1], atr):
            return False
        return self._bullish_structure_shift(london_candles, sweep)

    def _sell_confirmed(
        self,
        london_candles: list[Candle],
        sweep: Candle,
        asian_range: AsianSessionRange,
        atr: float,
    ) -> bool:
        after_sweep = self._candles_after_sweep(london_candles, sweep)
        if not after_sweep:
            return False
        latest = london_candles[-1]
        if latest.close >= asian_range.high:
            return False
        if not self._bearish_confirmation(after_sweep[-1], atr):
            return False
        return self._bearish_structure_shift(london_candles, sweep)

    def _candles_after_sweep(self, candles: list[Candle], sweep: Candle) -> list[Candle]:
        return [candle for candle in candles if candle.timestamp >= sweep.timestamp]

    def _bullish_confirmation(self, candle: Candle, atr: float) -> bool:
        displacement = body_size(candle) >= atr * self.settings.displacement_atr_multiplier
        return is_bullish_rejection(candle) or displacement

    def _bearish_confirmation(self, candle: Candle, atr: float) -> bool:
        displacement = body_size(candle) >= atr * self.settings.displacement_atr_multiplier
        return is_bearish_rejection(candle) or displacement

    def _bullish_structure_shift(self, candles: list[Candle], sweep: Candle) -> bool:
        prior = [candle for candle in candles if candle.timestamp < sweep.timestamp]
        after = self._candles_after_sweep(candles, sweep)
        if len(prior) < 3 or not after:
            return False
        swing_high = max(candle.high for candle in prior[-5:])
        return after[-1].close > swing_high

    def _bearish_structure_shift(self, candles: list[Candle], sweep: Candle) -> bool:
        prior = [candle for candle in candles if candle.timestamp < sweep.timestamp]
        after = self._candles_after_sweep(candles, sweep)
        if len(prior) < 3 or not after:
            return False
        swing_low = min(candle.low for candle in prior[-5:])
        return after[-1].close < swing_low

    def _build_buy(
        self,
        pair: str,
        london_candles: list[Candle],
        sweep: Candle,
        asian_range: AsianSessionRange,
        stop_buffer: float,
    ) -> TradeIdea | None:
        latest = london_candles[-1]
        entry = latest.close
        stop_loss = min(sweep.low, asian_range.low) - stop_buffer
        risk = entry - stop_loss
        if risk <= 0:
            return None
        take_profits = self._buy_targets(entry, risk, asian_range.high, london_candles)
        if not self._minimum_rr(entry, stop_loss, take_profits):
            return None
        return TradeIdea(
            pair=pair,
            direction=Direction.BUY,
            strategy=self.name,
            confidence=self._confidence(latest),
            entry=entry,
            stop_loss=stop_loss,
            take_profits=take_profits,
            risk_percent=0.5,
            explanation=(
                "London swept the Asian low, rejected back above the range, "
                "and closed through recent bullish structure."
            ),
        )

    def _build_sell(
        self,
        pair: str,
        london_candles: list[Candle],
        sweep: Candle,
        asian_range: AsianSessionRange,
        stop_buffer: float,
    ) -> TradeIdea | None:
        latest = london_candles[-1]
        entry = latest.close
        stop_loss = max(sweep.high, asian_range.high) + stop_buffer
        risk = stop_loss - entry
        if risk <= 0:
            return None
        take_profits = self._sell_targets(entry, risk, asian_range.low, london_candles)
        if not self._minimum_rr(entry, stop_loss, take_profits):
            return None
        return TradeIdea(
            pair=pair,
            direction=Direction.SELL,
            strategy=self.name,
            confidence=self._confidence(latest),
            entry=entry,
            stop_loss=stop_loss,
            take_profits=take_profits,
            risk_percent=0.5,
            explanation=(
                "London swept the Asian high, rejected back below the range, "
                "and closed through recent bearish structure."
            ),
        )

    def _buy_targets(
        self,
        entry: float,
        risk: float,
        asian_high: float,
        candles: list[Candle],
    ) -> list[float]:
        recent_high = max(candle.high for candle in candles[-20:])
        tp1 = max(entry + risk * self.settings.min_reward_to_risk, asian_high, recent_high)
        return [tp1, entry + risk * 2.5, entry + risk * 3.5]

    def _sell_targets(
        self,
        entry: float,
        risk: float,
        asian_low: float,
        candles: list[Candle],
    ) -> list[float]:
        recent_low = min(candle.low for candle in candles[-20:])
        tp1 = min(entry - risk * self.settings.min_reward_to_risk, asian_low, recent_low)
        return [tp1, entry - risk * 2.5, entry - risk * 3.5]

    def _minimum_rr(self, entry: float, stop_loss: float, take_profits: list[float]) -> bool:
        risk = abs(entry - stop_loss)
        reward = abs(take_profits[0] - entry)
        return bool(risk and reward / risk >= self.settings.min_reward_to_risk - 0.001)

    def _confidence(self, confirmation_candle: Candle) -> int:
        confidence = 85
        if candle_range(confirmation_candle) > 0:
            body_ratio = body_size(confirmation_candle) / candle_range(confirmation_candle)
            if body_ratio >= 0.6:
                confidence += 5
        return min(95, confidence)

    def _pip_size(self, pair: str) -> float:
        normalized = pair.upper().replace("/", "")
        if normalized.endswith("JPY"):
            return 0.01
        if normalized.startswith("XAU"):
            return 0.1
        return 0.0001
