import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.sms import SMSMessage
from app.gateway.http_gateway import HttpSMSGateway
from app.dlq.redis_dlq import publish_to_dlq
from app.db.mongo import sms_collection

logger = logging.getLogger("app.service.sms_processor")
gateway = HttpSMSGateway()

IST = ZoneInfo("Asia/Kolkata")


async def process_message(payload: dict):
    sms = SMSMessage(**payload)

    now = datetime.now(IST)

    # 1️⃣ Ensure document exists (idempotent by correlation_id)
    doc = await sms_collection.find_one_and_update(
        {"correlation_id": sms.correlation_id},
        {
            "$setOnInsert": {
                "correlation_id": sms.correlation_id,
                "event_code": sms.event_code,
                "recipient": sms.recipient,
                "message": sms.body,
                "created_at": now,
                "retry_count": 0,
                "attempts": [],
            },
            "$set": {
                "updated_at": now,
                "status": "PENDING",
            },
        },
        upsert=True,
        return_document=True,
    )

    retry_count = doc.get("retry_count", 0)
    attempt_no = retry_count + 1

    try:
        logger.info(
            "Sending SMS correlation_id=%s attempt=%s",
            sms.correlation_id,
            attempt_no,
        )

        gateway_result = await gateway.send_sms(sms)

        if not gateway_result["success"]:
            raise Exception(gateway_result["error"])

        # 2️⃣ SUCCESS
        await sms_collection.update_one(
            {"correlation_id": sms.correlation_id},
            {
                "$set": {
                    "status": "SUCCESS",
                    "updated_at": datetime.now(IST),
                },
                "$push": {
                    "attempts": {
                        "attempt": attempt_no,
                        "timestamp": datetime.now(IST),
                        "status": "SUCCESS",
                        "error": None,
                    }
                },
            },
        )

    except Exception as e:
        logger.exception(
            "SMS failed correlation_id=%s attempt=%s",
            sms.correlation_id,
            attempt_no,
        )

        # 3️⃣ FAILURE
        await sms_collection.update_one(
            {"correlation_id": sms.correlation_id},
            {
                "$set": {
                    "status": "FAILED",
                    "error": str(e),
                    "updated_at": datetime.now(IST),
                },
                "$inc": {"retry_count": 1},
                "$push": {
                    "attempts": {
                        "attempt": attempt_no,
                        "timestamp": datetime.now(IST),
                        "status": "FAILED",
                        "error": str(e),
                    }
                },
            },
        )

        await publish_to_dlq(payload, str(e))
        raise
