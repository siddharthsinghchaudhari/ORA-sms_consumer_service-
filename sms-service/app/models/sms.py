from pydantic import BaseModel
from typing import Optional, Dict


class SMSMessage(BaseModel):
    correlation_id: str
    event_code: str
    channel: str
    recipient: str
    subject: Optional[str]
    body: str
    metadata: Dict = {}
