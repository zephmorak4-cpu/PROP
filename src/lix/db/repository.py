from supabase import Client, create_client

from lix.config import Settings
from lix.domain.models import ActiveTrade, PairRank, TradeIdea, TradeUpdate


class Repository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Client | None = None
        if settings.supabase_configured:
            self.client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    async def save_signal(self, idea: TradeIdea) -> None:
        if not self.client:
            return
        self.client.table("lix_signals").insert(idea.model_dump(mode="json")).execute()

    async def create_active_trade(self, trade: ActiveTrade) -> None:
        if not self.client:
            return
        self.client.table("lix_active_trades").insert(trade.model_dump(mode="json")).execute()

    async def active_trade_exists(self, trade: ActiveTrade) -> bool:
        if not self.client:
            return False
        result = (
            self.client.table("lix_active_trades")
            .select("id")
            .eq("status", "active")
            .eq("pair", trade.pair)
            .eq("direction", trade.direction.value)
            .eq("strategy", trade.strategy)
            .limit(1)
            .execute()
        )
        return bool(result.data)

    async def list_active_trades(self) -> list[ActiveTrade]:
        if not self.client:
            return []
        result = (
            self.client.table("lix_active_trades")
            .select("*")
            .eq("status", "active")
            .execute()
        )
        return [ActiveTrade.model_validate(row) for row in result.data or []]

    async def update_active_trade_state(
        self,
        pair: str,
        opened_at: str,
        reached_targets: list[int],
        break_even_sent: bool,
        emergency_exit_sent: bool,
    ) -> None:
        if not self.client:
            return
        self.client.table("lix_active_trades").update(
            {
                "reached_targets": reached_targets,
                "break_even_sent": break_even_sent,
                "emergency_exit_sent": emergency_exit_sent,
            }
        ).eq("pair", pair).eq("opened_at", opened_at).execute()

    async def close_active_trade(self, pair: str, opened_at: str) -> None:
        if not self.client:
            return
        self.client.table("lix_active_trades").update({"status": "closed"}).eq("pair", pair).eq(
            "opened_at", opened_at
        ).execute()

    async def save_trade_update(self, update: TradeUpdate) -> None:
        if not self.client:
            return
        self.client.table("lix_trade_updates").insert(update.model_dump(mode="json")).execute()

    async def save_pair_rankings(self, rankings: list[PairRank]) -> None:
        if not self.client:
            return
        rows = [rank.model_dump(mode="json") for rank in rankings]
        if rows:
            self.client.table("lix_pair_rankings").insert(rows).execute()

    async def get_runtime_state(self, key: str):
        if not self.client:
            return None
        result = self.client.table("lix_runtime_state").select("value").eq("key", key).limit(1).execute()
        if not result.data:
            return None
        return result.data[0].get("value")

    async def set_runtime_state(self, key: str, value) -> None:
        if not self.client:
            return
        self.client.table("lix_runtime_state").upsert({"key": key, "value": value}).execute()
