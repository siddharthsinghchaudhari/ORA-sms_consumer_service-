import json
from app.queue.redis_client import redis_client

DLQ_STREAM = "queue:sms:otp:dlq"


async def publish_to_dlq(payload: dict, error: str):
    payload["error"] = error
    await redis_client.xadd(
        DLQ_STREAM,
        {"data": json.dumps(payload)},
    )
