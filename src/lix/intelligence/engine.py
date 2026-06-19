from lix.config import Settings
from lix.domain.models import StrategyContext, TradeIdea
from lix.intelligence.confidence import ConfidenceScoringEngine
from lix.intelligence.performance_memory import PerformanceMemory
from lix.intelligence.regime import MarketRegimeEngine
from lix.providers.market_data_provider import MarketDataProvider
from lix.risk.manager import RiskManager
from lix.strategies.asian_liquidity_sweep import AsianLiquiditySweepEngine
from lix.strategies.base import StrategyEngine
from lix.strategies.key_level_rejection import KeyLevelRejectionEngine
from lix.strategies.liquidity_grab import LiquidityGrabEngine
from lix.strategies.london_expansion import LondonExpansionEngine
from lix.strategies.monday_gap import MondayGapEngine
from lix.strategies.news_continuation import NewsContinuationEngine
from lix.strategies.volatility_expansion import VolatilityExpansionEngine


class LixIntelligenceEngine:
    """The only active decision engine in LI-X."""

    def __init__(self, settings: Settings, market_data: MarketDataProvider):
        self.settings = settings
        self.market_data = market_data
        self.regime_engine = MarketRegimeEngine()
        self.confidence_engine = ConfidenceScoringEngine()
        self.performance_memory = PerformanceMemory()
        self.risk_manager = RiskManager(settings.min_signal_confidence)
        self.strategies: list[StrategyEngine] = sorted(
            [
                AsianLiquiditySweepEngine(),
                KeyLevelRejectionEngine(),
                LondonExpansionEngine(),
                LiquidityGrabEngine(),
                VolatilityExpansionEngine(),
                NewsContinuationEngine(),
                MondayGapEngine(),
            ],
            key=lambda strategy: strategy.priority,
            reverse=True,
        )

    async def scan_pair(self, pair: str, timeframe: str = "15m") -> TradeIdea | None:
        candles = await self.market_data.get_candles(pair, timeframe=timeframe, limit=200)
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
