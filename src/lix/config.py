from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    log_level: str = "INFO"

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_admin_ids: list[str] = Field(default_factory=list)

    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    alpha_vantage_api_key: str | None = None
    finnhub_api_key: str | None = None
    financial_modeling_prep_api_key: str | None = None
    twelve_data_api_key: str | None = None
    openai_api_key: str | None = None

    monitored_pairs: list[str] = Field(
        default_factory=lambda: ["EURUSD", "GBPUSD", "USDJPY", "GBPJPY", "EURJPY", "XAUUSD"]
    )
    max_priority_pairs: int = 4
    min_signal_confidence: int = 85
    scheduler_enabled: bool = True
    admin_api_key: str | None = None
    signal_cooldown_minutes: int = 240
    trade_expiry_hours: int = 12
    asian_session_start_hour_utc: int = 0
    asian_session_end_hour_utc: int = 5
    london_session_start_hour_utc: int = 7
    london_session_end_hour_utc: int = 12
    atr_period: int = 14
    min_atr_pips: float = 4.0
    sweep_buffer_atr_multiplier: float = 0.08
    stop_buffer_atr_multiplier: float = 0.15
    displacement_atr_multiplier: float = 1.2
    min_reward_to_risk: float = 1.5
    max_spread_pips: float = 3.0
    news_block_minutes: int = 30

    @field_validator("monitored_pairs", "telegram_admin_ids", mode="before")
    @classmethod
    def parse_csv(cls, value):
        if value is None:
            return []
        if isinstance(value, int):
            return [str(value)]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def telegram_configured(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
