import logging

from lix.config import Settings
from lix.db.repository import Repository
from lix.domain.models import ActiveTrade, TradeIdea
from lix.intelligence.engine import LixIntelligenceEngine
from lix.telegram.client import TelegramClient

logger = logging.getLogger(__name__)


class MarketScanner:
    def __init__(
        self,
        settings: Settings,
        engine: LixIntelligenceEngine,
        repository: Repository,
        telegram: TelegramClient,
    ):
        self.settings = settings
        self.engine = engine
        self.repository = repository
        self.telegram = telegram

    async def scan(self) -> list[TradeIdea]:
        emitted: list[TradeIdea] = []
        for pair in self.settings.monitored_pairs:
            try:
                idea = await self.engine.scan_pair(pair)
            except Exception:
                logger.exception("LI-X scan failed for %s", pair)
                continue
            if not idea:
                continue
            active_trade = ActiveTrade.from_idea(idea)
            if await self.repository.active_trade_exists(active_trade):
                logger.info(
                    "Skipping duplicate active setup for %s %s %s",
                    idea.pair,
                    idea.direction.value,
                    idea.strategy,
                )
                continue
            await self.repository.save_signal(idea)
            await self.repository.create_active_trade(active_trade)
            await self.telegram.send_trade_idea(idea)
            emitted.append(idea)
        return emitted
