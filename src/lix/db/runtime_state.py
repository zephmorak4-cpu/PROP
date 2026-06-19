from typing import Any

from lix.db.repository import Repository


class SupabaseRuntimeState:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def get(self, key: str) -> Any | None:
        return await self.repository.get_runtime_state(key)

    async def set(self, key: str, value: Any) -> None:
        await self.repository.set_runtime_state(key, value)
