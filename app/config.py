from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "spimex_db"
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"

    REDIS_URL: RedisDsn = "redis://localhost:6379/0"

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    @property
    def database_url(self) -> str:
        """Собирает асинхронный DSN для PostgreSQL."""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.DB_USER,
                password=self.DB_PASS,
                host=self.DB_HOST,
                port=self.DB_PORT,
                path=self.DB_NAME,
            )
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",          
    )


settings = Settings()
