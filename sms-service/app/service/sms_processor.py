import json
import logging

from app.models.sms import SMSMessage
from app.gateway.http_gateway import HttpSMSGateway
from app.dlq.publisher import publish_to_dlq

logger = logging.getLogger("app.service.sms_processor")

gateway = HttpSMSGateway()


async def process_message(msg):
    logger.info(
        "Entered process_message offset=%s partition=%s",
        msg.offset,
        msg.partition,
    )

    try:
        payload = json.loads(msg.value)
        sms = SMSMessage(**payload)

        logger.info(
            "Sending SMS correlation_id=%s recipient=%s event_code=%s",
            sms.correlation_id,
            sms.recipient,
            sms.event_code,
        )

        await gateway.send_sms(sms)

        logger.info(
            "SMS sent successfully correlation_id=%s",
            sms.correlation_id,
        )

    except Exception as e:
        logger.exception(
            "SMS processing failed offset=%s error=%s",
            msg.offset,
            str(e),
        )

        await publish_to_dlq(msg.value, str(e))
        raise
