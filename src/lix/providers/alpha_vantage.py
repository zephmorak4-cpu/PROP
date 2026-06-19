from datetime import UTC, datetime
from typing import Any

import httpx

from lix.domain.models import Candle
from lix.providers.market_data_provider import MarketDataProvider


class AlphaVantageProvider(MarketDataProvider):
    base_url = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str | None):
        self.api_key = api_key

    async def get_candles(self, pair: str, timeframe: str, limit: int = 200) -> list[Candle]:
        if not self.api_key:
            return []
        from_symbol, to_symbol = self._split_pair(pair)
        params = {
            "function": "FX_INTRADAY",
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
            "interval": self._map_timeframe(timeframe),
            "outputsize": "compact",
            "apikey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()
        return self._parse_intraday(pair, timeframe, payload, limit)

    async def get_current_price(self, pair: str) -> float | None:
        candles = await self.get_candles(pair=pair, timeframe="5m", limit=1)
        return candles[-1].close if candles else None

    async def get_spread(self, pair: str) -> float | None:
        return None

    def _parse_intraday(
        self, pair: str, timeframe: str, payload: dict[str, Any], limit: int
    ) -> list[Candle]:
        series_key = next((key for key in payload if "Time Series FX" in key), None)
        if not series_key:
            return []
        rows = payload[series_key]
        candles: list[Candle] = []
        for timestamp, values in rows.items():
            candles.append(
                Candle(
                    pair=pair,
                    timeframe=timeframe,
                    timestamp=datetime.fromisoformat(timestamp).replace(tzinfo=UTC),
                    open=float(values["1. open"]),
                    high=float(values["2. high"]),
                    low=float(values["3. low"]),
                    close=float(values["4. close"]),
                )
            )
        return sorted(candles, key=lambda candle: candle.timestamp)[-limit:]

    def _split_pair(self, pair: str) -> tuple[str, str]:
        normalized = pair.upper().replace("/", "")
        if len(normalized) == 6:
            return normalized[:3], normalized[3:]
        if normalized == "XAUUSD":
            return "XAU", "USD"
        raise ValueError(f"Unsupported forex pair format: {pair}")

    def _map_timeframe(self, timeframe: str) -> str:
        mapping = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "60m": "60min",
            "1h": "60min",
        }
        return mapping.get(timeframe, "15min")
