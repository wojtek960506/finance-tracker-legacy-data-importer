from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from app.core.config import settings


async def init_db(app: FastAPI):
  """Attach MongoDB client and DB to the FastAPI app."""
  print(settings.MONGO_URI)

  client = AsyncIOMotorClient(settings.MONGO_URI)
  db_name = settings.MONGO_DB
  app.mongodb_client = client
  app.mongodb = client[db_name]
  print(f"Connected to MongoDB [{db_name}]")


def close_db(app: FastAPI):
  """Cleanly close the MongoDB client."""
  app.mongodb_client.close()
  print("Disconnected from MongoDB")
