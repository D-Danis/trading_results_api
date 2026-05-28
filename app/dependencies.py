from fastapi import Query
from fastapi import Request

from app.cache import RedisCache
from app.schemas import TradingFilter


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


async def get_cache(request: Request) -> RedisCache:
    return request.app.state.cache