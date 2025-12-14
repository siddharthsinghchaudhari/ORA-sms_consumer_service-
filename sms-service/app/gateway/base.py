from abc import ABC, abstractmethod
from app.models.sms import SMSMessage

class GatewayClient(ABC):
    @abstractmethod
    async def send_sms(self, sms: SMSMessage) -> None:
        pass
