import redis
from rq import Queue
from app.config import settings

redis_conn = redis.from_url(settings.REDIS_URL)

sms_queue = Queue(
    name="queue:sms:otp",
    connection=redis_conn,
)
