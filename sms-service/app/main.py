import asyncio
import logging
from fastapi import FastAPI
from prometheus_client import start_http_server

from app.kafka.consumer import start_consumer
from app.dlq.publisher import init_producer
from app.config import settings
from app.logging import setup_logging

app = FastAPI()

logger = logging.getLogger("app.main")


@app.on_event("startup")
async def startup():
    setup_logging()
    logger.info("SMS service starting up")

    # Start Prometheus metrics server ONCE
    start_http_server(settings.METRICS_PORT)
    logger.info(f"Metrics server started on port {settings.METRICS_PORT}")

    # Init DLQ producer
    await init_producer()
    logger.info("DLQ producer initialized")

    # Start Kafka consumer in background
    asyncio.create_task(start_consumer())
    logger.info("Kafka consumer task started")


@app.get("/health")
def health():
    return {"status": "ok"}
