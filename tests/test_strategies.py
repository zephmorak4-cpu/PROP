from datetime import UTC, datetime, timedelta

import pytest

from lix.config import Settings
from lix.domain.models import Candle, Direction, StrategyContext
from lix.strategies.asian_liquidity_sweep import AsianLiquiditySweepEngine


def make_asian_sweep_candles(direction: Direction = Direction.BUY) -> list[Candle]:
    start = datetime(2026, 6, 28, 21, 0, tzinfo=UTC)
    candles: list[Candle] = []
    for index in range(44):
        timestamp = start + timedelta(minutes=15 * index)
        open_price = 1.1000
        high = 1.1010
        low = 1.0990
        close = 1.1000

        if direction == Direction.BUY and timestamp == datetime(2026, 6, 29, 7, 30, tzinfo=UTC):
            open_price = 1.0994
            high = 1.1002
            low = 1.0978
            close = 1.0997
        if direction == Direction.BUY and timestamp == datetime(2026, 6, 29, 7, 45, tzinfo=UTC):
            open_price = 1.0997
            high = 1.1028
            low = 1.0994
            close = 1.1025

        if direction == Direction.SELL and timestamp == datetime(2026, 6, 29, 7, 30, tzinfo=UTC):
            open_price = 1.1006
            high = 1.1022
            low = 1.0998
            close = 1.1003
        if direction == Direction.SELL and timestamp == datetime(2026, 6, 29, 7, 45, tzinfo=UTC):
            open_price = 1.1003
            high = 1.1006
            low = 1.0972
            close = 1.0975

        candles.append(
            Candle(
                pair="EURUSD",
                timeframe="15m",
                timestamp=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=close,
            )
        )
    return candles


@pytest.mark.asyncio
async def test_asian_sweep_detects_london_low_sweep_buy():
    engine = AsianLiquiditySweepEngine(Settings())

    idea = await engine.evaluate(
        StrategyContext(pair="EURUSD", candles=make_asian_sweep_candles(Direction.BUY))
    )

    assert idea is not None
    assert idea.direction == Direction.BUY
    assert idea.strategy == "Asian Liquidity Sweep"
    assert idea.confidence >= 85


@pytest.mark.asyncio
async def test_asian_sweep_detects_london_high_sweep_sell():
    engine = AsianLiquiditySweepEngine(Settings())

    idea = await engine.evaluate(
        StrategyContext(pair="EURUSD", candles=make_asian_sweep_candles(Direction.SELL))
    )

    assert idea is not None
    assert idea.direction == Direction.SELL
    assert idea.confidence >= 85


@pytest.mark.asyncio
async def test_asian_sweep_rejects_non_london_signal():
    engine = AsianLiquiditySweepEngine(Settings())
    candles = make_asian_sweep_candles(Direction.BUY)
    candles[-1] = candles[-1].model_copy(update={"timestamp": datetime(2026, 6, 29, 13, 0, tzinfo=UTC)})

    idea = await engine.evaluate(StrategyContext(pair="EURUSD", candles=candles))

    assert idea is None
