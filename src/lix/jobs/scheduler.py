import asyncio
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from lix.config import Settings
from lix.db.repository import Repository
from lix.intelligence.engine import LixIntelligenceEngine
from lix.providers.fallback_market_data import FallbackMarketDataProvider
from lix.providers.fmp_market_data import FinancialModelingPrepMarketDataProvider
from lix.providers.news_provider import NewsProvider
from lix.providers.twelve_data_market_data import TwelveDataMarketDataProvider
from lix.services.market_scanner import MarketScanner
from lix.services.pair_ranking_service import PairRankingService
from lix.services.reporting import ReportingService
from lix.services.trade_monitor import TradeMonitor
from lix.telegram.client import TelegramClient

logger = logging.getLogger(__name__)


class LixScheduler:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self.market_data = FallbackMarketDataProvider(
            [
                TwelveDataMarketDataProvider(settings.twelve_data_api_key),
                FinancialModelingPrepMarketDataProvider(settings.financial_modeling_prep_api_key),
            ]
        )
        self.news_provider = NewsProvider(
            settings.financial_modeling_prep_api_key,
            settings.finnhub_api_key,
        )
        self.engine = LixIntelligenceEngine(
            settings=settings,
            market_data=self.market_data,
            news_provider=self.news_provider,
        )
        self.telegram = TelegramClient(settings)
        self.repository = Repository(settings)
        self.market_scanner = MarketScanner(settings, self.engine, self.repository, self.telegram)
        self.pair_ranking = PairRankingService(settings, self.market_data, self.repository)
        self.reporting = ReportingService(self.repository, self.telegram)
        self.trade_monitor = TradeMonitor(self.repository, self.telegram, self.market_data, settings)

    def start(self) -> None:
        self.scheduler.add_job(self.scan_market, "interval", minutes=1, id="lix_market_scan")
        self.scheduler.add_job(self.refresh_pair_rankings, "interval", minutes=5, id="lix_pair_ranking")
        self.scheduler.add_job(self.evaluate_trade_health, "interval", minutes=1, id="lix_trade_health")
        self.scheduler.add_job(self.send_daily_report, "cron", hour=21, minute=55, id="lix_daily_report")
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def scan_market(self) -> None:
        asyncio.run(self._scan_market())

    async def _scan_market(self) -> None:
        await self.market_scanner.scan()

    def refresh_pair_rankings(self) -> None:
        asyncio.run(self._refresh_pair_rankings())

    async def _refresh_pair_rankings(self) -> None:
        try:
            await self.pair_ranking.refresh()
        except Exception:
            logger.exception("LI-X pair ranking refresh failed")

    def evaluate_trade_health(self) -> None:
        asyncio.run(self._evaluate_trade_health())

    async def _evaluate_trade_health(self) -> None:
        try:
            updates = await self.trade_monitor.evaluate()
            for update in updates:
                await self.repository.save_trade_update(update)
                await self.telegram.send_trade_update(update)
        except Exception:
            logger.exception("LI-X trade health evaluation failed")

    def send_daily_report(self) -> None:
        asyncio.run(self._send_daily_report())

    async def _send_daily_report(self) -> None:
        try:
            await self.reporting.send_daily_report()
        except Exception:
            logger.exception("LI-X daily report failed")
