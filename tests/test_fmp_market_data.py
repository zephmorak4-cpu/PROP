from lix.providers.fmp_market_data import FinancialModelingPrepMarketDataProvider


def test_fmp_parses_stable_forex_candles():
    provider = FinancialModelingPrepMarketDataProvider(api_key="test")

    candles = provider._parse_candles(
        "EURUSD",
        "5m",
        [
            {
                "date": "2026-06-26 16:55:00",
                "open": 1.13818,
                "low": 1.13814,
                "high": 1.13863,
                "close": 1.1385,
                "volume": 248,
            }
        ],
        limit=10,
    )

    assert len(candles) == 1
    assert candles[0].pair == "EURUSD"
    assert candles[0].close == 1.1385


def test_fmp_ignores_error_payload():
    provider = FinancialModelingPrepMarketDataProvider(api_key="test")

    candles = provider._parse_candles("EURUSD", "5m", {"Error Message": "bad"}, limit=10)

    assert candles == []
