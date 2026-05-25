from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import RedisCache, get_cache
from app.database import get_session
from app.repository.trading import get_dynamics, get_last_trading_dates, get_trading_results
from app.schemas import LastTradingDatesList, TradingResultList, TradingResultOut

router = APIRouter()


@router.get("/last_trading_dates", response_model=LastTradingDatesList)
async def last_trading_dates(
    limit: int = Query(..., description="Количество последних торговых дней", ge=1, le=365),
    session: AsyncSession = Depends(get_session),
    cache: RedisCache = Depends(get_cache),
):
    """Возвращает список дат последних торговых дней."""
    cache_key = f"last_dates:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        return LastTradingDatesList.parse_raw(cached)
    dates = await get_last_trading_dates(session, limit)
    result = LastTradingDatesList(dates=dates)
    await cache.set(cache_key, result.model_dump_json(), ex=3600)  # TTL=1 час, но флеш в 14:11 перезатрёт
    return result


@router.get("/dynamics", response_model=TradingResultList)
async def dynamics(
    start_date: date = Query(..., description="Начальная дата (включительно)"),
    end_date: date = Query(..., description="Конечная дата (включительно)"),
    oil_id: str | None = Query(None, min_length=1, max_length=4),
    delivery_type_id: str | None = Query(None, min_length=1, max_length=1),
    delivery_basis_id: str | None = Query(None, min_length=1, max_length=3),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    cache: RedisCache = Depends(get_cache),
):
    """Возвращает торги за заданный период с возможной фильтрацией."""
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date не может быть позже end_date")

    # Ключ кэша на основе параметров
    cache_key = f"dynamics:{start_date}:{end_date}:{oil_id}:{delivery_type_id}:{delivery_basis_id}:{limit}:{offset}"
    cached = await cache.get(cache_key)
    if cached:
        return TradingResultList.parse_raw(cached)

    items, total = await get_dynamics(
        session, start_date, end_date, oil_id, delivery_type_id, delivery_basis_id, limit, offset
    )
    result = TradingResultList(
        items=[TradingResultOut.model_validate(item) for item in items],
        total=total,
    )
    await cache.set(cache_key, result.model_dump_json(), ex=3600)
    return result


@router.get("/trading_results", response_model=TradingResultList)
async def trading_results(
    oil_id: str | None = Query(None, min_length=1, max_length=4),
    delivery_type_id: str | None = Query(None, min_length=1, max_length=1),
    delivery_basis_id: str | None = Query(None, min_length=1, max_length=3),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    cache: RedisCache = Depends(get_cache),
):
    """Возвращает последние торги с фильтрацией (все параметры опциональны)."""
    cache_key = f"results:{oil_id}:{delivery_type_id}:{delivery_basis_id}:{limit}:{offset}"
    cached = await cache.get(cache_key)
    if cached:
        return TradingResultList.parse_raw(cached)

    items, total = await get_trading_results(session, oil_id, delivery_type_id, delivery_basis_id, limit, offset)
    result = TradingResultList(
        items=[TradingResultOut.model_validate(item) for item in items],
        total=total,
    )
    await cache.set(cache_key, result.model_dump_json(), ex=3600)
    return result
