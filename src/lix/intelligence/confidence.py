from lix.domain.models import MarketRegime, TradeIdea


class ConfidenceScoringEngine:
    def score(self, idea: TradeIdea, regime: MarketRegime, performance_adjustment: int = 0) -> TradeIdea:
        score = idea.confidence
        if regime == MarketRegime.NEWS_DRIVEN and idea.strategy != "News Continuation":
            score -= 15
        if regime == MarketRegime.LOW_VOLATILITY and "Expansion" not in idea.strategy:
            score -= 8
        score += performance_adjustment
        idea.confidence = max(0, min(100, score))
        return idea
