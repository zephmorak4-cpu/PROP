import httpx
import pytest

from lix.config import Settings
from lix.telegram.client import TelegramClient


class RejectingAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, json):
        request = httpx.Request("POST", url)
        response = httpx.Response(400, request=request, json={"ok": False})
        return response


@pytest.mark.asyncio
async def test_telegram_send_returns_false_on_api_rejection(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", RejectingAsyncClient)
    client = TelegramClient(
        Settings(telegram_bot_token="token", telegram_chat_id="123")
    )

    sent = await client.send_text("test")

    assert sent is False
