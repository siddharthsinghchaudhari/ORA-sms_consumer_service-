from dotenv import load_dotenv
import os

load_dotenv("/app/.env")  # load .env explicitly

from app.rq_queue.rq_connection import redis_conn
from app.service.sms_processor import process_sms

# IMPORTANT:
# Just importing is enough for RQ
