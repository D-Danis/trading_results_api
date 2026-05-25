import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.v1 import trading
from app.cache import RedisCache, schedule_flush, set_cache
from app.config import REDIS_URL

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("spimex_api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = RedisCache(REDIS_URL)
    set_cache(cache)                        # Сохраняем в глобальную переменную
    logger.info("Инициализация Redis")
    flush_task = asyncio.create_task(schedule_flush())
    yield
    # Завершение
    flush_task.cancel()
    try:
        await flush_task
    except asyncio.CancelledError:
        pass
    await cache.close()
    logger.info("Соединение с Redis закрыто")


app = FastAPI(
    title="SPIMEX Trading Results API",
    description="Сервис для получения данных о торгах нефтепродуктами",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(trading.router, prefix="/api/v1", tags=["trading"])
