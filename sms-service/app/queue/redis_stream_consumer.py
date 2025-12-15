import json
import logging
import asyncio

from app.queue.redis_client import redis_client
from app.service.sms_processor import process_message
from app.config import settings

logger = logging.getLogger("app.redis.consumer")


STREAM = "queue:sms:otp"
GROUP = settings.REDIS_STREAM_GROUP
CONSUMER = settings.REDIS_CONSUMER_NAME


async def ensure_group():
    try:
        await redis_client.xgroup_create(
            STREAM,
            GROUP,
            id="0",
            mkstream=True,
        )
    except Exception as e:
        if "BUSYGROUP" not in str(e):
            raise


async def consume():
    await ensure_group()
    logger.info("Redis stream consumer started")

    while True:
        messages = await redis_client.xreadgroup(
            groupname=GROUP,
            consumername=CONSUMER,
            streams={STREAM: ">"},
            count=1,
            block=5000,
        )

        if not messages:
            continue

        for stream_name, entries in messages:
            for message_id, fields in entries:
                try:
                    payload = json.loads(fields["data"])

                    # Attach redis metadata
                    payload["_redis_message_id"] = message_id

                    await process_message(payload)

                    # ACK only on success
                    await redis_client.xack(STREAM, GROUP, message_id)

                except Exception as e:
                    logger.exception(
                        "Processing failed redis_id=%s error=%s",
                        message_id,
                        str(e),
                    )
                    # DO NOT ACK → message remains pending
