from lix.providers.twelve_data_market_data import TwelveDataMarketDataProvider


def test_twelve_data_parses_forex_candles():
    provider = TwelveDataMarketDataProvider(api_key="test")

    candles = provider._parse_candles(
        "EURUSD",
        "15m",
        {
            "meta": {"symbol": "EUR/USD", "interval": "15min"},
            "values": [
                {
                    "datetime": "2026-06-29 23:00:00",
                    "open": "1.14014",
                    "high": "1.14055",
                    "low": "1.14013",
                    "close": "1.14048",
                }
            ],
        },
        limit=10,
    )

    assert len(candles) == 1
    assert candles[0].pair == "EURUSD"
    assert candles[0].close == 1.14048


def test_twelve_data_ignores_error_payload():
    provider = TwelveDataMarketDataProvider(api_key="test")

    candles = provider._parse_candles(
        "EURUSD",
        "15m",
        {"status": "error", "message": "bad"},
        limit=10,
    )

    assert candles == []


def test_twelve_data_maps_forex_symbols():
    provider = TwelveDataMarketDataProvider(api_key="test")

    assert provider._map_symbol("EURUSD") == "EUR/USD"
    assert provider._map_symbol("XAUUSD") == "XAU/USD"
