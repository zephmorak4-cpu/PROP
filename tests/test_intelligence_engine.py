from datetime import UTC, datetime, timedelta

import pytest

from lix.config import Settings
from lix.domain.models import Candle
from lix.intelligence.engine import LixIntelligenceEngine
from lix.providers.market_data_provider import MarketDataProvider


class FakeProvider(MarketDataProvider):
    async def get_candles(self, pair: str, timeframe: str, limit: int = 200) -> list[Candle]:
        base_time = datetime.now(UTC) - timedelta(minutes=15 * 50)
        candles = []
        for index in range(50):
            close = 1.1000
            low = 1.0990
            high = 1.1010
            if index == 44:
                low = 1.0980
            if index >= 45:
                close = 1.0995
            candles.append(
                Candle(
                    pair=pair,
                    timeframe=timeframe,
                    timestamp=base_time + timedelta(minutes=15 * index),
                    open=1.1000,
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
        settings=Settings(min_signal_confidence=70),
        market_data=FakeProvider(),
    )

    idea = await engine.scan_pair("EURUSD")

    assert idea is not None
    assert idea.strategy == "Asian Liquidity Sweep"
