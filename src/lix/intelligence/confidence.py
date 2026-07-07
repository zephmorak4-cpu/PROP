from lix.domain.models import MarketRegime, TradeIdea


class ConfidenceScoringEngine:
    def score(self, idea: TradeIdea, regime: MarketRegime, performance_adjustment: int = 0) -> TradeIdea:
        score = idea.confidence
        if regime == MarketRegime.NEWS_DRIVEN:
            score -= 15
        if regime == MarketRegime.LOW_VOLATILITY:
            score -= 8
        score += performance_adjustment
        idea.confidence = max(0, min(100, score))
        return idea
