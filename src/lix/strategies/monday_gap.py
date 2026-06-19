from lix.domain.models import StrategyContext, TradeIdea
from lix.strategies.base import StrategyEngine


class MondayGapEngine(StrategyEngine):
    name = "Monday Gap Intelligence"
    priority = 40

    async def evaluate(self, context: StrategyContext) -> TradeIdea | None:
        return None
