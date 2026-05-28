import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import trading
from app.cache import RedisCache
from app.config import REDIS_URL


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("spimex_api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = RedisCache(REDIS_URL)
    app.state.cache = cache
    logger.info("Инициализация Redis")
    yield
    await cache.close()
    logger.info("Соединение с Redis закрыто")


app = FastAPI(
    title="SPIMEX Trading Results API",
    description="Сервис для получения данных о торгах нефтепродуктами",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(trading.router, prefix="/api/v1", tags=["trading"])
