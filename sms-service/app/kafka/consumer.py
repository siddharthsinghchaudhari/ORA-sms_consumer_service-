import asyncio
import logging
from aiokafka import AIOKafkaConsumer

from app.config import settings
from app.service.sms_processor import process_message

logger = logging.getLogger("app.kafka.consumer")


async def start_consumer():
    logger.info("Kafka consumer starting")

    consumer = AIOKafkaConsumer(
        settings.SMS_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.CONSUMER_GROUP,
        enable_auto_commit=False,
    )

    await consumer.start()
    logger.info("Kafka consumer started")

    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY)

    try:
        async for msg in consumer:
            logger.info(
                "Message received topic=%s partition=%s offset=%s",
                msg.topic,
                msg.partition,
                msg.offset,
            )

            await semaphore.acquire()
            asyncio.create_task(
                handle_message(msg, consumer, semaphore)
            )

    except Exception:
        logger.exception("Kafka consumer crashed")

    finally:
        logger.info("Stopping Kafka consumer")
        await consumer.stop()


async def handle_message(msg, consumer, semaphore):
    try:
        logger.info("Processing message offset=%s", msg.offset)

        await process_message(msg)

        await consumer.commit()
        logger.info("Message committed offset=%s", msg.offset)

    except Exception:
        logger.exception("Message processing failed offset=%s", msg.offset)

    finally:
        semaphore.release()
