from datetime import UTC, datetime
from typing import Any

import httpx

from lix.domain.models import Candle
from lix.providers.market_data_provider import MarketDataProvider


class TwelveDataMarketDataProvider(MarketDataProvider):
    base_url = "https://api.twelvedata.com/time_series"

    def __init__(self, api_key: str | None):
        self.api_key = api_key

    async def get_candles(self, pair: str, timeframe: str, limit: int = 200) -> list[Candle]:
        if not self.api_key:
            return []
        params = {
            "symbol": self._map_symbol(pair),
            "interval": self._map_timeframe(timeframe),
            "outputsize": str(limit),
            "apikey": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError):
            return []
        return self._parse_candles(pair, timeframe, payload, limit)

    async def get_current_price(self, pair: str) -> float | None:
        candles = await self.get_candles(pair=pair, timeframe="5m", limit=1)
        return candles[-1].close if candles else None

    async def get_spread(self, pair: str) -> float | None:
        return None

    def _parse_candles(
        self, pair: str, timeframe: str, payload: Any, limit: int
    ) -> list[Candle]:
        if not isinstance(payload, dict) or payload.get("status") == "error":
            return []
        rows = payload.get("values")
        if not isinstance(rows, list):
            return []

        candles: list[Candle] = []
        for row in rows:
            if not isinstance(row, dict) or not row.get("datetime"):
                continue
            try:
                candles.append(
                    Candle(
                        pair=pair,
                        timeframe=timeframe,
                        timestamp=datetime.fromisoformat(str(row["datetime"])).replace(tzinfo=UTC),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row["volume"]) if row.get("volume") is not None else None,
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue
        return sorted(candles, key=lambda candle: candle.timestamp)[-limit:]

    def _map_timeframe(self, timeframe: str) -> str:
        mapping = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "60m": "1h",
            "1h": "1h",
            "4h": "4h",
        }
        return mapping.get(timeframe, "15min")

    def _map_symbol(self, pair: str) -> str:
        normalized = pair.upper().replace("/", "")
        if len(normalized) == 6:
            return f"{normalized[:3]}/{normalized[3:]}"
        if normalized == "XAUUSD":
            return "XAU/USD"
        return pair.upper()
