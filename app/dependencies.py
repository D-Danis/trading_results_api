from dataclasses import dataclass

from fastapi import Depends, Query
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.cache import RedisCache
from app.schemas import Pagination, TradingFilter
from app.repository.trading import TradingRepository


async def trading_filter(
    oil_id: str | None = Query(None, min_length=1, max_length=4, description="Код нефтепродукта"),
    delivery_type_id: str | None = Query(None, min_length=1, max_length=1, description="Тип поставки"),
    delivery_basis_id: str | None = Query(None, min_length=1, max_length=3, description="Базис поставки"),
) -> TradingFilter:
    return TradingFilter(
        oil_id=oil_id,
        delivery_type_id=delivery_type_id,
        delivery_basis_id=delivery_basis_id,
    )


async def pagination_params(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> Pagination:
    return Pagination(limit=limit, offset=offset)
 
 
async def get_cache(request: Request) -> RedisCache:
    return request.app.state.cache


async def get_repo(session: AsyncSession = Depends(get_session)) -> TradingRepository:
    return TradingRepository(session)
