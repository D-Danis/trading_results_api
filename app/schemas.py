import datetime

from pydantic import BaseModel, ConfigDict


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
    created_on: datetime.datetime
    updated_on: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class TradingResultList(BaseModel):
    """Список записей."""

    items: list[TradingResultOut]
    total: int


class LastTradingDatesList(BaseModel):
    """Список дат последних торговых дней."""

    dates: list[datetime.date]
