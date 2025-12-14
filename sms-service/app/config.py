from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "sms-consumer"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str

    SMS_TOPIC: str = "sms.otp"
    DLQ_TOPIC: str = "sms.dlq"

    CONSUMER_GROUP: str = "sms-consumer-group"
    MAX_CONCURRENCY: int = 10

    # Gateway
    SMS_GATEWAY_URL: str
    SMS_GATEWAY_API_KEY: str
    GATEWAY_TIMEOUT_SEC: int = 5
    GATEWAY_MAX_RETRIES: int = 3

    # Observability
    METRICS_PORT: int = 8001

    class Config:
        env_file = ".env"

settings = Settings()
