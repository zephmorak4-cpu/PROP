from lix.domain.models import ActiveTrade, Direction, TradeManagementAction
from lix.services.trade_monitor import TradeMonitor


def make_monitor() -> TradeMonitor:
    return TradeMonitor(repository=None, telegram=None, market_data=None)


def make_buy_trade() -> ActiveTrade:
    return ActiveTrade(
        pair="EURUSD",
        direction=Direction.BUY,
        strategy="Asian Liquidity Sweep",
        entry=1.1000,
        stop_loss=1.0950,
        take_profits=[1.1050, 1.1100, 1.1150],
        confidence=80,
        risk_percent=0.5,
    )


def test_trade_monitor_moves_to_break_even_at_tp1():
    trade = make_buy_trade()

    updates = make_monitor().evaluate_trade(trade, 1.1051)

    assert updates[0].action == TradeManagementAction.MOVE_TO_BREAK_EVEN
    assert trade.break_even_sent is True
    assert trade.reached_targets == [1]


def test_trade_monitor_closes_at_final_target():
    trade = make_buy_trade()
    trade.reached_targets = [1, 2]
    trade.break_even_sent = True

    updates = make_monitor().evaluate_trade(trade, 1.1160)

    assert updates[0].action == TradeManagementAction.FULL_TAKE_PROFIT
    assert trade.reached_targets == [1, 2, 3]


def test_trade_monitor_emergency_exit_on_stop_breach():
    trade = make_buy_trade()

    updates = make_monitor().evaluate_trade(trade, 1.0940)

    assert updates[0].action == TradeManagementAction.EMERGENCY_EXIT
    assert trade.emergency_exit_sent is True
