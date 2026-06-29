from lix.domain.models import Candle
from lix.providers.market_data_provider import MarketDataProvider


class FallbackMarketDataProvider(MarketDataProvider):
    def __init__(self, providers: list[MarketDataProvider]):
        self.providers = providers

    async def get_candles(self, pair: str, timeframe: str, limit: int = 200) -> list[Candle]:
        for provider in self.providers:
            candles = await provider.get_candles(pair, timeframe, limit)
            if candles:
                return candles
        return []

    async def get_current_price(self, pair: str) -> float | None:
        for provider in self.providers:
            price = await provider.get_current_price(pair)
            if price is not None:
                return price
        return None

    async def get_spread(self, pair: str) -> float | None:
        for provider in self.providers:
            spread = await provider.get_spread(pair)
            if spread is not None:
                return spread
        return None
