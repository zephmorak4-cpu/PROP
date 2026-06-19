from lix.domain.models import TradeIdea


class RiskManager:
    def __init__(self, min_confidence: int):
        self.min_confidence = min_confidence

    def approve(self, idea: TradeIdea) -> bool:
        if idea.confidence < self.min_confidence:
            return False
        if idea.risk_percent <= 0 or idea.risk_percent > 1:
            return False
        if not idea.take_profits:
            return False
        return True
