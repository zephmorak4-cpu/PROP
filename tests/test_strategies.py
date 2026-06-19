from datetime import UTC, datetime, timedelta

import pytest

from lix.domain.models import Candle, StrategyContext
from lix.strategies.liquidity_grab import LiquidityGrabEngine
from lix.strategies.london_expansion import LondonExpansionEngine


def make_candles(count: int, close: float = 1.1000) -> list[Candle]:
    start = datetime.now(UTC) - timedelta(minutes=15 * count)
    return [
        Candle(
            pair="EURUSD",
            timeframe="15m",
            timestamp=start + timedelta(minutes=15 * index),
            open=close,
            high=close + 0.0010,
            low=close - 0.0010,
            close=close,
        )
        for index in range(count)
    ]


@pytest.mark.asyncio
async def test_liquidity_grab_detects_equal_high_sweep():
    candles = make_candles(25)
    candles[-1] = candles[-1].model_copy(
        update={"open": 1.1000, "high": 1.1040, "low": 1.0990, "close": 1.1005}
    )

    idea = await LiquidityGrabEngine().evaluate(StrategyContext(pair="EURUSD", candles=candles))

    assert idea is not None
    assert idea.direction == "SELL"


@pytest.mark.asyncio
async def test_london_expansion_detects_breakout_displacement():
    candles = make_candles(30)
    candles[-1] = candles[-1].model_copy(
        update={"open": 1.1000, "high": 1.1045, "low": 1.0998, "close": 1.1040}
    )

    idea = await LondonExpansionEngine().evaluate(StrategyContext(pair="EURUSD", candles=candles))

    assert idea is not None
    assert idea.direction == "BUY"
