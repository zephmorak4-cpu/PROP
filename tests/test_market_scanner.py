import pytest

from lix.domain.models import ActiveTrade, Direction, TradeIdea
from lix.services.market_scanner import MarketScanner


class FakeEngine:
    async def scan_pair(self, pair: str):
        return TradeIdea(
            pair=pair,
            direction=Direction.BUY,
            strategy="London Expansion",
            confidence=75,
            entry=1.1,
            stop_loss=1.09,
            take_profits=[1.11, 1.12, 1.13],
            risk_percent=0.5,
            explanation="test",
        )


class FakeRepository:
    def __init__(self, exists: bool, recent: bool = False):
        self.exists = exists
        self.recent = recent
        self.saved = 0
        self.created = 0

    async def active_trade_exists(self, trade: ActiveTrade) -> bool:
        return self.exists

    async def recent_signal_exists(self, idea: TradeIdea, cooldown_minutes: int) -> bool:
        return self.recent

    async def save_signal(self, idea: TradeIdea) -> None:
        self.saved += 1

    async def create_active_trade(self, trade: ActiveTrade) -> None:
        self.created += 1


class FakeTelegram:
    def __init__(self):
        self.sent = 0

    async def send_trade_idea(self, idea: TradeIdea) -> bool:
        self.sent += 1
        return True


class FakeSettings:
    monitored_pairs = ["EURUSD"]
    signal_cooldown_minutes = 240


@pytest.mark.asyncio
async def test_market_scanner_skips_duplicate_active_setup():
    repository = FakeRepository(exists=True)
    telegram = FakeTelegram()
    scanner = MarketScanner(FakeSettings(), FakeEngine(), repository, telegram)

    emitted = await scanner.scan()

    assert emitted == []
    assert repository.saved == 0
    assert repository.created == 0
    assert telegram.sent == 0


@pytest.mark.asyncio
async def test_market_scanner_emits_new_setup():
    repository = FakeRepository(exists=False)
    telegram = FakeTelegram()
    scanner = MarketScanner(FakeSettings(), FakeEngine(), repository, telegram)

    emitted = await scanner.scan()

    assert len(emitted) == 1
    assert repository.saved == 1
    assert repository.created == 1
    assert telegram.sent == 1


@pytest.mark.asyncio
async def test_market_scanner_skips_recent_setup_inside_cooldown():
    repository = FakeRepository(exists=False, recent=True)
    telegram = FakeTelegram()
    scanner = MarketScanner(FakeSettings(), FakeEngine(), repository, telegram)

    emitted = await scanner.scan()

    assert emitted == []
    assert repository.saved == 0
    assert repository.created == 0
    assert telegram.sent == 0
