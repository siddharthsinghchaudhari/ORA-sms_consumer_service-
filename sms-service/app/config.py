from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "sms-consumer"

    # # Kafka
    # KAFKA_BOOTSTRAP_SERVERS: str

    # SMS_TOPIC: str = "sms.otp"
    # DLQ_TOPIC: str = "sms.dlq"

    # CONSUMER_GROUP: str = "sms-consumer-group"
    MAX_CONCURRENCY: int = 10

    # Redis
    REDIS_URL: str

    REDIS_STREAM_GROUP: str
    REDIS_CONSUMER_NAME: str

    REDIS_STREAM_PREFIX: str

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
