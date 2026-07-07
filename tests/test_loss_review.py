from lix.domain.models import ActiveTrade, Direction
from lix.monitoring.loss_review import LossReviewEngine


def test_loss_review_marks_stop_hunt_when_trade_later_reaches_target():
    trade = ActiveTrade(
        pair="EURUSD",
        direction=Direction.BUY,
        strategy="Asian Liquidity Sweep",
        entry=1.1000,
        stop_loss=1.0950,
        take_profits=[1.1075, 1.1125, 1.1175],
        confidence=88,
        risk_percent=0.5,
    )

    review = LossReviewEngine().review(trade, later_reached_target=True)

    assert review.stopped_hunted is True
    assert review.confidence_justified is False
