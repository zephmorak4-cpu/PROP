from abc import ABC, abstractmethod

from lix.domain.models import StrategyContext, TradeIdea


class StrategyEngine(ABC):
    name: str
    priority: int

    @abstractmethod
    async def evaluate(self, context: StrategyContext) -> TradeIdea | None:
        """Return a trade idea or None if the setup is not valid."""
