from lix.domain.models import StrategyContext, TradeIdea
from lix.strategies.base import StrategyEngine


class NewsContinuationEngine(StrategyEngine):
    name = "News Continuation"
    priority = 50

    async def evaluate(self, context: StrategyContext) -> TradeIdea | None:
        return None
