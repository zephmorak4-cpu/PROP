from fastapi.testclient import TestClient

from lix.config import get_settings
from lix.main import app


class FakeTelegram:
    async def send_text(self, text: str) -> bool:
        return "LI-X System Test" in text

    async def send_trade_update(self, update) -> bool:
        return True


class FakeMarketScanner:
    async def scan(self) -> list:
        return []


class FakePairRanking:
    async def refresh(self) -> list:
        return []


class FakeTradeMonitor:
    async def evaluate(self) -> list:
        return []


class FakeRepository:
    async def save_trade_update(self, update) -> None:
        return None


class FakeScheduler:
    telegram = FakeTelegram()
    market_scanner = FakeMarketScanner()
    pair_ranking = FakePairRanking()
    trade_monitor = FakeTradeMonitor()
    repository = FakeRepository()

    def shutdown(self) -> None:
        return None


def override_settings():
    settings = get_settings()
    settings.admin_api_key = "test-admin"
    settings.scheduler_enabled = False
    return settings


def test_admin_endpoint_requires_key():
    app.dependency_overrides[get_settings] = override_settings
    with TestClient(app) as client:
        client.app.state.scheduler = FakeScheduler()
        response = client.post("/admin/test-telegram")

    app.dependency_overrides.clear()

    assert response.status_code == 401


def test_admin_test_telegram_accepts_valid_key():
    app.dependency_overrides[get_settings] = override_settings
    with TestClient(app) as client:
        client.app.state.scheduler = FakeScheduler()
        response = client.post("/admin/test-telegram", headers={"X-Admin-Key": "test-admin"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"sent": True}
