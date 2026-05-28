from datetime import datetime

from sqlalchemy import String, Integer, BigInteger, DateTime, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SpimexTradingResult(Base):
    __tablename__ = "spimex_trading_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exchange_product_id: Mapped[str] = mapped_column(String(11), nullable=False)
    exchange_product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    oil_id: Mapped[str] = mapped_column(String(4), nullable=False)
    delivery_basis_id: Mapped[str] = mapped_column(String(3), nullable=False)
    delivery_basis_name: Mapped[str] = mapped_column(String(300), nullable=False)
    delivery_type_id: Mapped[str] = mapped_column(String(1), nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(BigInteger, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("exchange_product_id", "date", name="uq_product_date"),
        Index("ix_date", "date"),
        Index("ix_exchange_product_id", "exchange_product_id"),
    )
