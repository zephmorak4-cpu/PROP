from datetime import UTC, datetime, timedelta

import pytest

from lix.config import Settings
from lix.domain.models import Candle
from lix.intelligence.engine import LixIntelligenceEngine
from lix.providers.market_data_provider import MarketDataProvider


class FakeProvider(MarketDataProvider):
    async def get_candles(self, pair: str, timeframe: str, limit: int = 200) -> list[Candle]:
        base_time = datetime(2026, 6, 28, 21, 0, tzinfo=UTC)
        candles = []
        for index in range(44):
            close = 1.1000
            open_price = 1.1000
            low = 1.0990
            high = 1.1010
            timestamp = base_time + timedelta(minutes=15 * index)
            if timestamp == datetime(2026, 6, 29, 7, 30, tzinfo=UTC):
                open_price = 1.0994
                high = 1.1002
                low = 1.0978
                close = 1.0997
            if timestamp == datetime(2026, 6, 29, 7, 45, tzinfo=UTC):
                open_price = 1.0997
                high = 1.1028
                low = 1.0994
                close = 1.1025
            candles.append(
                Candle(
                    pair=pair,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close,
                )
            )
        return candles

    async def get_current_price(self, pair: str) -> float | None:
        return 1.1

    async def get_spread(self, pair: str) -> float | None:
        return None


@pytest.mark.asyncio
async def test_engine_returns_single_lix_trade_idea():
    engine = LixIntelligenceEngine(
        settings=Settings(min_signal_confidence=85),
        market_data=FakeProvider(),
    )

    idea = await engine.scan_pair("EURUSD")

    assert idea is not None
    assert idea.strategy == "Asian Liquidity Sweep"
