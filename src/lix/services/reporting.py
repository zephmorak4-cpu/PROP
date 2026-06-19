from datetime import UTC, date, datetime

from lix.db.repository import Repository
from lix.telegram.client import TelegramClient


class ReportingService:
    def __init__(self, repository: Repository, telegram: TelegramClient):
        self.repository = repository
        self.telegram = telegram

    async def send_daily_report(self, report_date: date | None = None) -> bool:
        target_date = report_date or datetime.now(UTC).date()
        text = (
            "<b>LI-X Daily Report</b>\n\n"
            f"Date: {target_date.isoformat()}\n"
            "Status: reporting pipeline online.\n"
            "Performance aggregation will use Supabase signal and trade lifecycle records."
        )
        return await self.telegram.send_text(text)

    async def send_weekly_report(self) -> bool:
        text = (
            "<b>LI-X Weekly Report</b>\n\n"
            "Status: weekly reporting pipeline online.\n"
            "Strategy, pair, and market regime analysis will aggregate stored outcomes."
        )
        return await self.telegram.send_text(text)
