from datetime import UTC, datetime, timedelta

from lix.config import Settings
from lix.domain.models import StrategyContext, TradeIdea
from lix.intelligence.confidence import ConfidenceScoringEngine
from lix.intelligence.performance_memory import PerformanceMemory
from lix.intelligence.regime import MarketRegimeEngine
from lix.providers.market_data_provider import MarketDataProvider
from lix.providers.news_provider import EconomicEvent, NewsProvider
from lix.risk.manager import RiskManager
from lix.strategies.asian_liquidity_sweep import AsianLiquiditySweepEngine
from lix.strategies.base import StrategyEngine


class LixIntelligenceEngine:
    """Single-strategy decision engine for LI-X v2."""

    def __init__(
        self,
        settings: Settings,
        market_data: MarketDataProvider,
        news_provider: NewsProvider | None = None,
    ):
        self.settings = settings
        self.market_data = market_data
        self.news_provider = news_provider
        self.regime_engine = MarketRegimeEngine()
        self.confidence_engine = ConfidenceScoringEngine()
        self.performance_memory = PerformanceMemory()
        self.risk_manager = RiskManager(settings.min_signal_confidence)
        self.strategies: list[StrategyEngine] = [AsianLiquiditySweepEngine(settings)]
        self._news_cache: list[EconomicEvent] = []
        self._news_cache_until: datetime | None = None

    async def scan_pair(self, pair: str, timeframe: str = "15m") -> TradeIdea | None:
        candles = await self.market_data.get_candles(pair, timeframe=timeframe, limit=200)
        if await self._news_blocked(pair):
            return None
        if await self._spread_blocked(pair):
            return None
        regime = self.regime_engine.classify(candles)
        context = StrategyContext(pair=pair, candles=candles, regime=regime)

        for strategy in self.strategies:
            idea = await strategy.evaluate(context)
            if not idea:
                continue
            adjustment = await self.performance_memory.strategy_adjustment(pair, idea.strategy)
            scored = self.confidence_engine.score(idea, regime, adjustment)
            if self.risk_manager.approve(scored):
                return scored
        return None

    async def _news_blocked(self, pair: str) -> bool:
        if not self.news_provider or self.settings.news_block_minutes <= 0:
            return False
        events = await self._high_impact_events()
        now = datetime.now(UTC)
        blocked_window = timedelta(minutes=self.settings.news_block_minutes)
        pair_currencies = self._pair_currencies(pair)
        for event in events:
            if abs(event.scheduled_at - now) > blocked_window:
                continue
            event_key = event.country.upper()
            if event_key in pair_currencies or any(currency in event_key for currency in pair_currencies):
                return True
        return False

    async def _high_impact_events(self) -> list[EconomicEvent]:
        now = datetime.now(UTC)
        if self._news_cache_until and now < self._news_cache_until:
            return self._news_cache
        try:
            self._news_cache = await self.news_provider.high_impact_events() if self.news_provider else []
        except Exception:
            self._news_cache = []
        self._news_cache_until = now + timedelta(minutes=5)
        return self._news_cache

    async def _spread_blocked(self, pair: str) -> bool:
        spread = await self.market_data.get_spread(pair)
        if spread is None:
            return False
        return spread > self.settings.max_spread_pips * self._pip_size(pair)

    def _pair_currencies(self, pair: str) -> set[str]:
        normalized = pair.upper().replace("/", "")
        if normalized == "XAUUSD":
            return {"XAU", "USD", "US", "UNITED STATES"}
        if len(normalized) == 6:
            return {normalized[:3], normalized[3:], self._country_key(normalized[:3]), self._country_key(normalized[3:])}
        return {normalized}

    def _country_key(self, currency: str) -> str:
        mapping = {
            "USD": "US",
            "EUR": "EU",
            "GBP": "UK",
            "JPY": "JP",
        }
        return mapping.get(currency, currency)

    def _pip_size(self, pair: str) -> float:
        normalized = pair.upper().replace("/", "")
        if normalized.endswith("JPY"):
            return 0.01
        if normalized.startswith("XAU"):
            return 0.1
        return 0.0001
