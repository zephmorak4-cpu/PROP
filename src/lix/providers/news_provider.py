from dataclasses import dataclass
from datetime import UTC, datetime

import httpx


@dataclass(frozen=True)
class EconomicEvent:
    name: str
    country: str
    impact: str
    scheduled_at: datetime


class NewsProvider:
    base_url = "https://financialmodelingprep.com/api/v3/economic_calendar"

    def __init__(self, financial_modeling_prep_api_key: str | None, finnhub_api_key: str | None):
        self.financial_modeling_prep_api_key = financial_modeling_prep_api_key
        self.finnhub_api_key = finnhub_api_key

    async def high_impact_events(self) -> list[EconomicEvent]:
        if not self.financial_modeling_prep_api_key:
            return []
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                self.base_url,
                params={"apikey": self.financial_modeling_prep_api_key},
            )
            response.raise_for_status()
            payload = response.json()
        return [event for event in (self._parse_event(row) for row in payload) if event]

    def _parse_event(self, row: dict) -> EconomicEvent | None:
        impact = str(row.get("impact") or row.get("importance") or "").lower()
        name = str(row.get("event") or row.get("name") or "")
        if "high" not in impact and not any(
            keyword in name.upper() for keyword in ("CPI", "NFP", "FOMC", "INTEREST RATE")
        ):
            return None

        raw_date = row.get("date")
        if not raw_date:
            return None
        try:
            scheduled_at = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
        except ValueError:
            return None
        if not scheduled_at.tzinfo:
            scheduled_at = scheduled_at.replace(tzinfo=UTC)

        return EconomicEvent(
            name=name,
            country=str(row.get("country") or row.get("currency") or "unknown"),
            impact=impact or "high",
            scheduled_at=scheduled_at,
        )
