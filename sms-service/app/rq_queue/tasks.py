from app.service.sms_processor import process_sms

def enqueue_only(payload: dict):
    """
    RQ entrypoint.
    This function is what RQ imports and executes.
    """
    return process_sms(payload)


