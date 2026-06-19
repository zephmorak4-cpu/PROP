from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from lix.config import Settings, get_settings
from lix.jobs.scheduler import LixScheduler

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(
    settings: Annotated[Settings, Depends(get_settings)],
    x_admin_key: Annotated[str | None, Header(alias="X-Admin-Key")] = None,
) -> None:
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_API_KEY is not configured.",
        )
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key.",
        )


def get_scheduler(request: Request) -> LixScheduler:
    return request.app.state.scheduler


@router.post("/test-telegram", dependencies=[Depends(require_admin)])
async def test_telegram(scheduler: Annotated[LixScheduler, Depends(get_scheduler)]):
    sent = await scheduler.telegram.send_text(
        "<b>LI-X System Test</b>\n\nTelegram delivery is configured and reachable."
    )
    return {"sent": sent}


@router.post("/scan-now", dependencies=[Depends(require_admin)])
async def scan_now(scheduler: Annotated[LixScheduler, Depends(get_scheduler)]):
    ideas = await scheduler.market_scanner.scan()
    return {
        "signals": len(ideas),
        "ideas": [idea.model_dump(mode="json") for idea in ideas],
    }


@router.post("/pair-rankings/refresh", dependencies=[Depends(require_admin)])
async def refresh_pair_rankings(scheduler: Annotated[LixScheduler, Depends(get_scheduler)]):
    rankings = await scheduler.pair_ranking.refresh()
    return {
        "rankings": [ranking.model_dump(mode="json") for ranking in rankings],
    }


@router.post("/trade-health/evaluate", dependencies=[Depends(require_admin)])
async def evaluate_trade_health(scheduler: Annotated[LixScheduler, Depends(get_scheduler)]):
    updates = await scheduler.trade_monitor.evaluate()
    for update in updates:
        await scheduler.repository.save_trade_update(update)
        await scheduler.telegram.send_trade_update(update)
    return {
        "updates": [update.model_dump(mode="json") for update in updates],
    }
