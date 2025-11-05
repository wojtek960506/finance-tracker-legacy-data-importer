from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.utils.mongodb_fastapi import MongoDBFastAPI
import logging
import sys


async def init_db(app: MongoDBFastAPI):
  """Attach MongoDB client and DB to the FastAPI app."""
  client = AsyncIOMotorClient(settings.MONGO_URI)
  db_name = settings.MONGO_DB
  app.mongodb_client = client
  app.mongodb = client[db_name]
  
  logger = logging.getLogger("app")
  handler = logging.StreamHandler(sys.stdout)
  logger.addHandler(handler)
  logger.setLevel(logging.INFO)

  logger.info(f"Connected to MongoDB [{db_name}]")



def close_db(app: MongoDBFastAPI):
  """Cleanly close the MongoDB client."""
  app.mongodb_client.close()
  logging.debug("Disconnected from MongoDB")
