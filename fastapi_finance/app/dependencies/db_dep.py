from fastapi import Depends
from app.db.database import Database
from app.utils.mongodb_request import MongoDBRequest


async def get_db(request: MongoDBRequest) -> Database:
  return request.app.db
