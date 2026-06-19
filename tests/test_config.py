from lix.config import Settings


def test_csv_parsing():
    settings = Settings(monitored_pairs="EURUSD, GBPUSD", telegram_admin_ids="1,2")

    assert settings.monitored_pairs == ["EURUSD", "GBPUSD"]
    assert settings.telegram_admin_ids == ["1", "2"]


def test_supabase_runtime_state_is_the_default_store():
    settings = Settings()

    assert settings.supabase_configured is False
