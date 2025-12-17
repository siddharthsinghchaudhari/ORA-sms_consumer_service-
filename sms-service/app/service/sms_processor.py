import logging
from datetime import datetime
import pytz

from app.models.sms import SMSMessage
from app.gateway.http_gateway import HttpSMSGateway
from app.db.mongo_sync import sms_collection

logger = logging.getLogger("app.service.sms_processor")
gateway = HttpSMSGateway()

IST = pytz.timezone("Asia/Kolkata")


def ist_now():
    return datetime.now(IST)


def process_sms(payload: dict):
    sms = SMSMessage(**payload)
    now = ist_now()

    doc = sms_collection.find_one_and_update(
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

    attempt_no = doc.get("retry_count", 0) + 1

    try:
        logger.info(
            "Sending SMS correlation_id=%s attempt=%s",
            sms.correlation_id,
            attempt_no,
        )

        result = gateway.send_sms(sms)

        if not result["success"]:
            raise Exception(result["error"])

        sms_collection.update_one(
            {"correlation_id": sms.correlation_id},
            {
                "$set": {
                    "status": "SUCCESS",
                    "updated_at": ist_now(),
                },
                "$push": {
                    "attempts": {
                        "attempt": attempt_no,
                        "timestamp": ist_now(),
                        "status": "SUCCESS",
                        "error": None,
                    }
                },
            },
        )

    except Exception as e:
        sms_collection.update_one(
            {"correlation_id": sms.correlation_id},
            {
                "$set": {
                    "status": "FAILED",
                    "error": str(e),
                    "updated_at": ist_now(),
                },
                "$inc": {"retry_count": 1},
                "$push": {
                    "attempts": {
                        "attempt": attempt_no,
                        "timestamp": ist_now(),
                        "status": "FAILED",
                        "error": str(e),
                    }
                },
            },
        )

        logger.exception("SMS failed correlation_id=%s", sms.correlation_id)
        raise
