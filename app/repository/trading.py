import logging
from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SpimexTradingResult


async def get_last_trading_dates(
    session: AsyncSession,
    limit: int
) -> list[date]:
    """Возвращает список последних `limit` уникальных дат торгов."""
    stmt = select(SpimexTradingResult.date).distinct().order_by(SpimexTradingResult.date.desc()).limit(limit)
    result = await session.execute(stmt)
    logging.info(f"Resul: {result}")
    return [row[0] for row in result.all()]


async def get_dynamics(
    session: AsyncSession,
    start_date: date,
    end_date: date,
    oil_id: str | None = None,
    delivery_type_id: str | None = None,
    delivery_basis_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[SpimexTradingResult], int]:
    """Возвращает торги за период с фильтрами."""
    conditions = [
        SpimexTradingResult.date >= start_date,
        SpimexTradingResult.date <= end_date,
    ]
    if oil_id:
        conditions.append(SpimexTradingResult.oil_id == oil_id)
    if delivery_type_id:
        conditions.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id:
        conditions.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

    where_clause = and_(*conditions)

    count_stmt = select(func.count()).where(where_clause)
    total = (await session.execute(count_stmt)).scalar_one()

    stmt = (
        select(SpimexTradingResult)
        .where(where_clause)
        .order_by(SpimexTradingResult.date.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    items = result.scalars().all()
    return items, total


async def get_trading_results(
    session: AsyncSession,
    oil_id: str | None = None,
    delivery_type_id: str | None = None,
    delivery_basis_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[SpimexTradingResult], int]:
    """Возвращает последние торги с фильтрацией."""
    conditions = []
    if oil_id:
        conditions.append(SpimexTradingResult.oil_id == oil_id)
    if delivery_type_id:
        conditions.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id:
        conditions.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

    if conditions:
        where_clause = and_(*conditions)
    else:
        where_clause = True

    count_stmt = select(func.count()).where(where_clause)
    total = (await session.execute(count_stmt)).scalar_one()

    stmt = (
        select(SpimexTradingResult)
        .where(where_clause)
        .order_by(SpimexTradingResult.date.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    items = result.scalars().all()
    return items, total
