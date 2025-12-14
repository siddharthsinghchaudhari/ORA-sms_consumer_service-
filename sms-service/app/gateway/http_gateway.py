import asyncio
import logging
import httpx

from app.config import settings
from app.models.sms import SMSMessage
from app.gateway.base import GatewayClient

logger = logging.getLogger("app.gateway.http_sms")


class HttpSMSGateway(GatewayClient):

    async def send_sms(self, sms: SMSMessage) -> None:
        logger.info(
            "Calling SMS gateway correlation_id=%s",
            sms.correlation_id,
        )

        headers = {
            "Authorization": f"Bearer {settings.SMS_GATEWAY_API_KEY}",
            "X-Correlation-Id": sms.correlation_id,
            "Idempotency-Key": sms.correlation_id,
        }

        payload = {
            "to": sms.recipient,
            "message": sms.body,
        }

        async with httpx.AsyncClient(
            timeout=settings.GATEWAY_TIMEOUT_SEC
        ) as client:

            for attempt in range(settings.GATEWAY_MAX_RETRIES):
                try:
                    resp = await client.post(
                        settings.SMS_GATEWAY_URL,
                        json=payload,
                        headers=headers,
                    )

                    if resp.status_code == 429:
                        logger.warning(
                            "Gateway rate limited correlation_id=%s attempt=%s",
                            sms.correlation_id,
                            attempt + 1,
                        )
                        await asyncio.sleep(2 ** attempt)
                        continue

                    resp.raise_for_status()
                    return

                except Exception:
                    if attempt == settings.GATEWAY_MAX_RETRIES - 1:
                        logger.exception(
                            "Gateway failed correlation_id=%s",
                            sms.correlation_id,
                        )
                        raise

                    await asyncio.sleep(2 ** attempt)
