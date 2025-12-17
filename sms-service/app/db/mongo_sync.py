from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

sms_collection = db.sms_messages
