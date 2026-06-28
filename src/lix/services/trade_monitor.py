from lix.db.repository import Repository
from lix.domain.models import ActiveTrade, Direction, TradeManagementAction, TradeUpdate
from lix.providers.market_data_provider import MarketDataProvider
from lix.telegram.client import TelegramClient


class TradeMonitor:
    def __init__(
        self,
        repository: Repository,
        telegram: TelegramClient,
        market_data: MarketDataProvider,
    ):
        self.repository = repository
        self.telegram = telegram
        self.market_data = market_data

    async def evaluate(self) -> list[TradeUpdate]:
        updates: list[TradeUpdate] = []
        active_trades = await self.repository.list_active_trades()
        for trade in active_trades:
            price = await self.market_data.get_current_price(trade.pair)
            if price is None:
                continue
            trade_updates = self.evaluate_trade(trade, price)
            for update in trade_updates:
                await self._persist_trade_state(trade, update)
            updates.extend(trade_updates)
        return updates

    def evaluate_trade(self, trade: ActiveTrade, price: float) -> list[TradeUpdate]:
        updates: list[TradeUpdate] = []

        if self._stop_breached(trade, price) and not trade.emergency_exit_sent:
            trade.emergency_exit_sent = True
            updates.append(
                TradeUpdate(
                    pair=trade.pair,
                    action=TradeManagementAction.EMERGENCY_EXIT,
                    confidence=95,
                    reason="Price breached the protected stop-loss area.",
                )
            )
            return updates

        for index, target in enumerate(trade.take_profits, start=1):
            if index in trade.reached_targets or not self._target_reached(trade, price, target):
                continue
            trade.reached_targets.append(index)
            if index == 1 and not trade.break_even_sent:
                trade.break_even_sent = True
                updates.append(
                    TradeUpdate(
                        pair=trade.pair,
                        action=TradeManagementAction.MOVE_TO_BREAK_EVEN,
                        confidence=85,
                        reason="TP1 reached. Move stop loss to break-even and reduce open risk.",
                    )
                )
            elif index < len(trade.take_profits):
                updates.append(
                    TradeUpdate(
                        pair=trade.pair,
                        action=TradeManagementAction.PARTIAL_PROFIT,
                        confidence=82,
                        reason=f"TP{index} reached. Consider taking partial profit.",
                    )
                )
            else:
                updates.append(
                    TradeUpdate(
                        pair=trade.pair,
                        action=TradeManagementAction.FULL_TAKE_PROFIT,
                        confidence=90,
                        reason=f"Final target TP{index} reached. Close remaining position.",
                    )
                )

        return updates

    async def _persist_trade_state(self, trade: ActiveTrade, update: TradeUpdate) -> None:
        opened_at = trade.opened_at.isoformat()
        if update.action in {
            TradeManagementAction.FULL_TAKE_PROFIT,
            TradeManagementAction.EMERGENCY_EXIT,
        }:
            await self.repository.close_active_trade(trade.pair, opened_at)
            return
        await self.repository.update_active_trade_state(
            pair=trade.pair,
            opened_at=opened_at,
            reached_targets=trade.reached_targets,
            break_even_sent=trade.break_even_sent,
            emergency_exit_sent=trade.emergency_exit_sent,
        )

    def _target_reached(self, trade: ActiveTrade, price: float, target: float) -> bool:
        if trade.direction == Direction.BUY:
            return price >= target
        return price <= target

    def _stop_breached(self, trade: ActiveTrade, price: float) -> bool:
        if trade.direction == Direction.BUY:
            return price <= trade.stop_loss
        return price >= trade.stop_loss
