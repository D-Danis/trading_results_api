from datetime import date
from typing import Callable, Awaitable

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.cache import RedisCache, get_ttl_to_target
from app.dependencies import trading_filter, get_app_dependencies, AppDependencies
from app.schemas import LastTradingDatesList, TradingResultList, TradingResultOut, TradingFilter, T

router = APIRouter()


async def get_cached_or_fetch(
    cache: RedisCache,
    cache_key: str,
    fetch_func: Callable[[], Awaitable[T]],     
    response_model: type[T],
) -> T:
    cached = await cache.get(cache_key)
    if cached:
        return response_model.model_validate_json(cached)
            
    result = await fetch_func()
    
    ttl = get_ttl_to_target()
    await cache.set(cache_key, result.model_dump_json(), ex=ttl)
    
    return result
    

@router.get("/last_trading_dates", response_model=LastTradingDatesList)
async def last_trading_dates(
    limit: int = Query(..., description="Количество последних торговых дней", ge=1, le=365),
    deps: AppDependencies = Depends(get_app_dependencies), 
) -> LastTradingDatesList:
    """Возвращает список дат последних торговых дней."""
    cache_key = f"last_dates:{limit}"
    
    async def _fetch():
        dates = await deps.repo.get_last_trading_dates(limit)
        return LastTradingDatesList(dates=dates)

    return await get_cached_or_fetch(deps.cache, cache_key, _fetch, LastTradingDatesList)


@router.get("/dynamics", response_model=TradingResultList)
async def dynamics(
    start_date: date = Query(..., description="Начальная дата (включительно)"),
    end_date: date = Query(..., description="Конечная дата (включительно)"),
    filter: TradingFilter = Depends(trading_filter),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    deps: AppDependencies = Depends(get_app_dependencies), 
) -> TradingResultList:
    """Возвращает торги за заданный период с возможной фильтрацией."""
    if start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="start_date не может быть позже end_date")

    cache_key = f"dynamics:{start_date}:{end_date}:" + ":".join(
        str(v) for v in filter.model_dump().values()
    ) + f":{limit}:{offset}"

    async def _fetch():
        items, total = await deps.repo.get_dynamics(
            start_date, end_date, filter, limit, offset)
        return TradingResultList(
            items=[TradingResultOut.from_orm(item) for item in items],
            total=total,
        )
    return await get_cached_or_fetch(deps.cache, cache_key, _fetch, TradingResultList)


@router.get("/trading_results", response_model=TradingResultList)
async def trading_results(
    filter: TradingFilter = Depends(trading_filter),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    deps: AppDependencies = Depends(get_app_dependencies), 
):
    """Возвращает последние торги с фильтрацией (все параметры опциональны)."""
    cache_key = "results:" + ":".join(
        str(v) for v in filter.model_dump().values()
    ) + f":{limit}:{offset}"
 
    async def _fetch():
        items, total = await deps.repo.get_trading_results(filter, limit, offset)
        return TradingResultList(
            items=[TradingResultOut.from_orm(item) for item in items],
            total=total,
        )
    return await get_cached_or_fetch(deps.cache, cache_key, _fetch, TradingResultList)
