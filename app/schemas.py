import datetime
from typing import TypeVar

from pydantic import BaseModel, Field, AwareDatetime


T = TypeVar("T", bound=BaseModel)


class TradingResultOut(BaseModel):
    """Схема для выдачи одной записи."""

    id: int
    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: int
    total: int
    count: int
    date: datetime.date
    created_on: AwareDatetime
    updated_on: AwareDatetime

    @classmethod
    def from_orm(cls, orm_obj):
        return cls.model_validate({
            column.key: getattr(orm_obj, column.key)
            for column in orm_obj.__table__.columns
        })


class TradingResultList(BaseModel):
    """Список записей."""

    items: list[TradingResultOut]
    total: int


class LastTradingDatesList(BaseModel):
    """Список дат последних торговых дней."""

    dates: list[datetime.date]


class TradingFilter(BaseModel):
    oil_id: str | None = Field(None, min_length=1, max_length=4, description="Код нефтепродукта")
    delivery_type_id: str | None = Field(None, min_length=1, max_length=1, description="Тип поставки")
    delivery_basis_id: str | None = Field(None, min_length=1, max_length=3, description="Базис поставки")


class Pagination(BaseModel):
    limit: int = Field(100, ge=1, le=1000, description="Количество записей на странице")
    offset: int = Field(0, ge=0, description="Смещение для пагинации")

