from lix.domain.models import Candle, PairRank


class PairRankingEngine:
    def rank(self, market: dict[str, list[Candle]], limit: int) -> list[PairRank]:
        ranks: list[PairRank] = []
        for pair, candles in market.items():
            if len(candles) < 20:
                ranks.append(PairRank(pair=pair, score=0, reasons=["insufficient_data"]))
                continue
            ranges = [candle.high - candle.low for candle in candles[-20:]]
            volatility_score = min(80, int((sum(ranges) / len(ranges)) * 10000))
            score = max(1, min(100, volatility_score + 10))
            ranks.append(PairRank(pair=pair, score=score, reasons=["volatility_available"]))
        return sorted(ranks, key=lambda rank: rank.score, reverse=True)[:limit]
