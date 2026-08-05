from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:testtest123@localhost:5432/crypto"
    redis_url: str = "redis://127.0.0.1:6379"

    symbol: str = "BTCUSDT"
    spread_threshold: float = 0.05
    collect_interval: int = 30
    price_cache_ttl: int = 2
    alert_ttl: int = 900

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""


settings = Settings()
