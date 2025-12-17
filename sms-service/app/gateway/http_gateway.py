import logging
import requests

from app.config import settings
from app.models.sms import SMSMessage

logger = logging.getLogger("app.gateway.http_sms")


class HttpSMSGateway:
    """
    Synchronous SMS Gateway client for RQ workers.
    Uses settings from .env for URL and API key.
    """

    def __init__(self):
        self.url = settings.SMS_GATEWAY_URL
        self.api_key = settings.SMS_GATEWAY_API_KEY
        self.timeout = getattr(settings, "GATEWAY_TIMEOUT_SEC", 5)
        self.max_retries = getattr(settings, "GATEWAY_MAX_RETRIES", 3)

    def send_sms(self, sms: SMSMessage):
        """
        Send SMS synchronously.
        Returns a dict: {"success": bool, "error": str, "attempt": int, "status_code": int}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Correlation-Id": sms.correlation_id,
            "Idempotency-Key": sms.correlation_id,
        }

        payload = {
            "to": sms.recipient,
            "message": sms.body,
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    "Sending SMS correlation_id=%s attempt=%s",
                    sms.correlation_id,
                    attempt,
                )

                resp = requests.post(
                    self.url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )

                if resp.status_code == 429:
                    # Too Many Requests → exponential backoff
                    logger.warning(
                        "Rate limited by gateway, correlation_id=%s, retry=%s",
                        sms.correlation_id,
                        attempt,
                    )
                    backoff = 2 ** attempt
                    import time

                    time.sleep(backoff)
                    continue

                resp.raise_for_status()

                return {"success": True, "attempt": attempt, "status_code": resp.status_code}

            except Exception as e:
                logger.exception(
                    "SMS send failed correlation_id=%s attempt=%s",
                    sms.correlation_id,
                    attempt,
                )
                if attempt == self.max_retries:
                    return {"success": False, "attempt": attempt, "error": str(e)}

                import time

                time.sleep(2 ** attempt)
