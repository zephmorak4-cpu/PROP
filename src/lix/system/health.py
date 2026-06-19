from lix.config import Settings


def build_health_report(settings: Settings) -> dict:
    missing_required = []
    degraded = []

    if not settings.telegram_configured:
        missing_required.append("telegram")
    if not settings.supabase_configured:
        missing_required.append("supabase")
    if not settings.alpha_vantage_api_key:
        missing_required.append("alpha_vantage")

    if not settings.financial_modeling_prep_api_key:
        degraded.append("financial_modeling_prep")
    if not settings.finnhub_api_key:
        degraded.append("finnhub")

    return {
        "status": "ok" if not missing_required else "degraded",
        "decision_engine": "LI-X Intelligence Engine",
        "runtime_state_store": "supabase",
        "missing_required": missing_required,
        "degraded_optional": degraded,
    }
