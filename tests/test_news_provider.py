from lix.providers.news_provider import NewsProvider


def test_fmp_parser_keeps_high_impact_event():
    provider = NewsProvider(financial_modeling_prep_api_key="test", finnhub_api_key=None)

    event = provider._parse_event(
        {
            "event": "CPI Inflation Rate",
            "country": "US",
            "impact": "High",
            "date": "2026-06-18T12:30:00Z",
        }
    )

    assert event is not None
    assert event.name == "CPI Inflation Rate"
    assert event.country == "US"


def test_fmp_parser_drops_low_impact_event():
    provider = NewsProvider(financial_modeling_prep_api_key="test", finnhub_api_key=None)

    event = provider._parse_event(
        {
            "event": "Minor Business Survey",
            "country": "US",
            "impact": "Low",
            "date": "2026-06-18T12:30:00Z",
        }
    )

    assert event is None
