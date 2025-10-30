from fastapi import Request
from app.utils.mongodb_fastapi import MongoDBFastAPI

class MongoDBRequest(Request):
  app: MongoDBFastAPI
