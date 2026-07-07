from lix.config import Settings


def test_csv_parsing():
    settings = Settings(monitored_pairs="EURUSD, GBPUSD", telegram_admin_ids="1,2")

    assert settings.monitored_pairs == ["EURUSD", "GBPUSD"]
    assert settings.telegram_admin_ids == ["1", "2"]


def test_numeric_admin_id_is_coerced_to_list():
    settings = Settings(telegram_admin_ids=6780870656)

    assert settings.telegram_admin_ids == ["6780870656"]


def test_supabase_runtime_state_is_the_default_store():
    settings = Settings()

    assert settings.supabase_configured is False


def test_v2_default_confidence_requires_high_quality_setups():
    settings = Settings()

    assert settings.min_signal_confidence == 85
