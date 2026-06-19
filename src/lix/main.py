from contextlib import asynccontextmanager

from fastapi import FastAPI

from lix.api.admin import router as admin_router
from lix.config import Settings, get_settings
from lix.jobs.scheduler import LixScheduler
from lix.system.health import build_health_report


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    scheduler = LixScheduler(settings=settings)
    app.state.scheduler = scheduler
    if settings.scheduler_enabled:
        scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(
    title="LI-X Institutional Forex Intelligence",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(admin_router)


@app.get("/health")
async def health():
    return build_health_report(get_settings())


@app.get("/config/runtime")
async def runtime_config():
    settings: Settings = get_settings()
    return {
        "environment": settings.environment,
        "monitored_pairs": settings.monitored_pairs,
        "max_priority_pairs": settings.max_priority_pairs,
        "min_signal_confidence": settings.min_signal_confidence,
        "runtime_state_store": "supabase",
        "telegram_configured": settings.telegram_configured,
        "supabase_configured": settings.supabase_configured,
        "alpha_vantage_configured": bool(settings.alpha_vantage_api_key),
        "finnhub_configured": bool(settings.finnhub_api_key),
        "financial_modeling_prep_configured": bool(settings.financial_modeling_prep_api_key),
        "openai_configured": bool(settings.openai_api_key),
    }
