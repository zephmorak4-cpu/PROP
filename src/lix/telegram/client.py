import httpx
import logging

from lix.config import Settings
from lix.domain.models import TradeIdea, TradeUpdate

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def send_text(self, text: str) -> bool:
        if not self.settings.telegram_configured:
            return False
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.settings.telegram_chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError:
                logger.exception("Telegram message rejected by Telegram API")
                return False
            except httpx.HTTPError:
                logger.exception("Telegram message delivery failed")
                return False
        return True

    async def send_trade_idea(self, idea: TradeIdea) -> bool:
        return await self.send_text(format_trade_idea(idea))

    async def send_trade_update(self, update: TradeUpdate) -> bool:
        return await self.send_text(
            f"<b>LI-X Trade Update</b>\n\n"
            f"Pair: {update.pair}\n"
            f"Action: {update.action.value}\n"
            f"Confidence: {update.confidence}/100\n"
            f"Reason: {update.reason}"
        )


def format_trade_idea(idea: TradeIdea) -> str:
    tps = "\n".join(f"TP{index}: {price:.5f}" for index, price in enumerate(idea.take_profits, 1))
    return (
        f"<b>LI-X Entry Signal</b>\n\n"
        f"Pair: {idea.pair}\n"
        f"Direction: {idea.direction.value}\n"
        f"Strategy: {idea.strategy}\n"
        f"Confidence: {idea.confidence}/100\n\n"
        f"Entry: {idea.entry:.5f}\n"
        f"Stop Loss: {idea.stop_loss:.5f}\n"
        f"{tps}\n\n"
        f"Risk: {idea.risk_percent:.2f}%\n"
        f"Reason: {idea.explanation}"
    )
