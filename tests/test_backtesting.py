from datetime import UTC, datetime, timedelta

import pytest

from lix.backtesting.engine import AsianSweepBacktester
from lix.config import Settings
from lix.domain.models import Candle


def make_candles() -> list[Candle]:
    start = datetime(2026, 6, 28, 21, 0, tzinfo=UTC)
    candles: list[Candle] = []
    for index in range(220):
        timestamp = start + timedelta(minutes=15 * index)
        candles.append(
            Candle(
                pair="EURUSD",
                timeframe="15m",
                timestamp=timestamp,
                open=1.1000,
                high=1.1010,
                low=1.0990,
                close=1.1000,
            )
        )
    return candles


@pytest.mark.asyncio
async def test_backtester_returns_empty_metrics_without_setups():
    result = await AsianSweepBacktester(Settings()).run("EURUSD", make_candles(), window=40)

    assert result.pair == "EURUSD"
    assert result.total_setups == 0
    assert result.average_confidence == 0
