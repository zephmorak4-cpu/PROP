from abc import ABC, abstractmethod

from lix.domain.models import Candle


class MarketDataProvider(ABC):
    @abstractmethod
    async def get_candles(self, pair: str, timeframe: str, limit: int = 200) -> list[Candle]:
        """Return normalized forex candles for a pair and timeframe."""

    @abstractmethod
    async def get_current_price(self, pair: str) -> float | None:
        """Return latest known mid price."""

    @abstractmethod
    async def get_spread(self, pair: str) -> float | None:
        """Return current spread when the provider supports it."""
