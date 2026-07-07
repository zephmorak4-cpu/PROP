from dataclasses import dataclass

from lix.domain.models import ActiveTrade


@dataclass(frozen=True)
class LossReview:
    pair: str
    strategy: str
    stopped_hunted: bool
    news_nearby: bool
    volatility_too_low: bool
    london_session_weak: bool
    later_reached_target: bool
    confidence_justified: bool
    review_notes: str


class LossReviewEngine:
    def review(
        self,
        trade: ActiveTrade,
        *,
        news_nearby: bool = False,
        volatility_too_low: bool = False,
        later_reached_target: bool = False,
    ) -> LossReview:
        stopped_hunted = later_reached_target
        confidence_justified = not (news_nearby or volatility_too_low or stopped_hunted)
        notes = self._notes(news_nearby, volatility_too_low, stopped_hunted, later_reached_target)
        return LossReview(
            pair=trade.pair,
            strategy=trade.strategy,
            stopped_hunted=stopped_hunted,
            news_nearby=news_nearby,
            volatility_too_low=volatility_too_low,
            london_session_weak=False,
            later_reached_target=later_reached_target,
            confidence_justified=confidence_justified,
            review_notes=notes,
        )

    def _notes(
        self,
        news_nearby: bool,
        volatility_too_low: bool,
        stopped_hunted: bool,
        later_reached_target: bool,
    ) -> str:
        reasons: list[str] = []
        if news_nearby:
            reasons.append("High-impact news was near the trade.")
        if volatility_too_low:
            reasons.append("Volatility was below the configured threshold.")
        if stopped_hunted:
            reasons.append("Price later reached target after breaching the stop area.")
        if later_reached_target and not stopped_hunted:
            reasons.append("Trade later reached target after invalidation.")
        return " ".join(reasons) or "No obvious loss-quality issue detected."
