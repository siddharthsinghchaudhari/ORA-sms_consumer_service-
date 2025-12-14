import json
import logging
from aiokafka import AIOKafkaProducer
from app.config import settings

logger = logging.getLogger("app.dlq.publisher")

producer: AIOKafkaProducer | None = None


async def init_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )
    await producer.start()
    logger.info("DLQ producer ready")


async def publish_to_dlq(raw_value: bytes, error: str):
    """
    raw_value: Kafka message value (bytes)
    """
    try:
        message = json.loads(raw_value)

        message["dlq_error"] = error

        await producer.send_and_wait(
            settings.DLQ_TOPIC,
            json.dumps(message).encode("utf-8"),
        )

        logger.error(
            "Message sent to DLQ correlation_id=%s error=%s",
            message.get("correlation_id"),
            error,
        )

    except Exception:
        logger.exception("Failed to publish message to DLQ")
