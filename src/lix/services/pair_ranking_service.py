from lix.config import Settings
from lix.db.repository import Repository
from lix.domain.models import PairRank
from lix.intelligence.pair_ranking import PairRankingEngine
from lix.providers.market_data_provider import MarketDataProvider


class PairRankingService:
    def __init__(self, settings: Settings, market_data: MarketDataProvider, repository: Repository):
        self.settings = settings
        self.market_data = market_data
        self.repository = repository
        self.ranking_engine = PairRankingEngine()

    async def refresh(self) -> list[PairRank]:
        market = {}
        for pair in self.settings.monitored_pairs:
            market[pair] = await self.market_data.get_candles(pair, timeframe="15m", limit=80)
        rankings = self.ranking_engine.rank(market, self.settings.max_priority_pairs)
        await self.repository.save_pair_rankings(rankings)
        return rankings
