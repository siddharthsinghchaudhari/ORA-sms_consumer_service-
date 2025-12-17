from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "sms-consumer"

    MAX_CONCURRENCY: int = 10

    # Redis
    REDIS_URL: str

    # Gateway
    SMS_GATEWAY_URL: str
    SMS_GATEWAY_API_KEY: str
    GATEWAY_TIMEOUT_SEC: int = 5
    GATEWAY_MAX_RETRIES: int = 3

    # Observability
    METRICS_PORT: int = 8001

    # Mongo
    MONGO_URI: str
    MONGO_DB: str

    class Config:
        env_file = ".env"

settings = Settings()
