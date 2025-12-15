import asyncio
import logging
from fastapi import FastAPI
from prometheus_client import start_http_server

from app.queue.redis_stream_consumer import consume

from app.config import settings
from app.log_config import setup_logging

app = FastAPI()

logger = logging.getLogger("app.main")


@app.on_event("startup")
async def startup():
    setup_logging()
    logger.info("SMS service starting up")

    # Start Prometheus metrics server ONCE
    start_http_server(settings.METRICS_PORT)
    logger.info(f"Metrics server started on port {settings.METRICS_PORT}")

    # Start Redis stream consumer
    asyncio.create_task(consume())
    logger.info("Redis stream consumer task started")


@app.get("/health")
def health():
    return {"status": "ok"}
