# SPIMEX Trading Results API

Микросервис на FastAPI для отдачи данных о результатах торгов нефтепродуктами СПбМТСБ в формате JSON.  
Использует PostgreSQL как источник данных и Redis для кэширования.

## Эндпоинты

- `GET /api/v1/last_trading_dates` – список последних торговых дней (параметр `limit` обязателен).
- `GET /api/v1/dynamics` – торги за период с фильтрами (`start_date`, `end_date` обязательны; `oil_id`, `delivery_basis_id`, `delivery_type_id` опциональны).
- `GET /api/v1/trading_results` – последние торги с опциональными фильтрами (`oil_id`, `delivery_basis_id`, `delivery_type_id`).

Кэш всех запросов хранится в Redis до **14:11** каждого дня, затем полностью сбрасывается.

## Требования

- Python 3.12+
- PostgreSQL (с таблицей `spimex_trading_results`, заполненной парсером)
- Redis (для кэширования)

## Быстрый старт

### 1. Установка зависимостей

```bash
uv sync
```

### 2. Конфигурация

Создайте файл `.env` в корне проекта:

```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=spimex_db
DB_USER=postgres
DB_PASS=your_password
REDIS_URL=redis://localhost:6379/0
```

### 3. Запуск Redis (через Docker)

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 4. Запуск микросервиса

```bash
uv run python main.py
```

Сервер стартует на `http://0.0.0.0:8000`.  
Swagger-документация доступна по адресу `http://localhost:8000/docs`.
