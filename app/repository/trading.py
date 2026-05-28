from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SpimexTradingResult
from app.schemas import TradingFilter 


class TradingRepository:
    """Репозиторий для работы с результатами торгов SPIMEX."""

    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_last_trading_dates(self, limit: int) -> list[date]:
        """Возвращает список последних `limit` уникальных дат торгов."""
        stmt = (
            select(SpimexTradingResult.date)
            .distinct()
            .order_by(SpimexTradingResult.date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    
    async def get_dynamics(
        self,
        start_date: date,
        end_date: date,
        filter: TradingFilter | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[SpimexTradingResult], int]:
        """Возвращает торги за период с учётом фильтров."""
        conditions = [
            SpimexTradingResult.date >= start_date,
            SpimexTradingResult.date <= end_date,
        ]
        if filter:
            if filter.oil_id:
                conditions.append(SpimexTradingResult.oil_id == filter.oil_id)
            if filter.delivery_type_id:
                conditions.append(SpimexTradingResult.delivery_type_id == filter.delivery_type_id)
            if filter.delivery_basis_id:
                conditions.append(SpimexTradingResult.delivery_basis_id == filter.delivery_basis_id)

        where_clause = and_(*conditions)

        count_stmt = select(func.count()).where(where_clause)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(SpimexTradingResult)
            .where(where_clause)
            .order_by(SpimexTradingResult.date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        return items, total

    
    async def get_trading_results(
        self,
        filter: TradingFilter | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[SpimexTradingResult], int]:
        """Возвращает последние торги с фильтрацией (все параметры опциональны)."""
        conditions = []
        if filter:
            if filter.oil_id:
                conditions.append(SpimexTradingResult.oil_id == filter.oil_id)
            if filter.delivery_type_id:
                conditions.append(SpimexTradingResult.delivery_type_id == filter.delivery_type_id)
            if filter.delivery_basis_id:
                conditions.append(SpimexTradingResult.delivery_basis_id == filter.delivery_basis_id)

        if conditions:
            where_clause = and_(*conditions)
        else:
            where_clause = True

        count_stmt = select(func.count()).where(where_clause)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(SpimexTradingResult)
            .where(where_clause)
            .order_by(SpimexTradingResult.date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        return items, total
