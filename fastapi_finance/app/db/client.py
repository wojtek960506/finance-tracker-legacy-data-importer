from contextlib import asynccontextmanager
from typing import AsyncIterator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from app.db.database import Database
from app.utils.mongodb_fastapi import MongoDBFastAPI
import logging
import sys


logger = logging.getLogger("app")
if not logger.handlers:
  handler = logging.StreamHandler(sys.stdout)
  logger.addHandler(handler)
logger.setLevel(logging.INFO)


def create_mongo_client(mongo_uri: str | None = None) -> AsyncIOMotorClient:
  return AsyncIOMotorClient(mongo_uri or settings.MONGO_URI)


def get_mongo_database(
  client: AsyncIOMotorClient,
  db_name: str | None = None,
) -> AsyncIOMotorDatabase:
  return client[db_name or settings.MONGO_DB]


@asynccontextmanager
async def database_session(
  mongo_uri: str | None = None,
  db_name: str | None = None,
) -> AsyncIterator[Database]:
  client = create_mongo_client(mongo_uri)
  resolved_db_name = db_name or settings.MONGO_DB
  database = Database(get_mongo_database(client, resolved_db_name))
  logger.info(f"Connected to MongoDB [{resolved_db_name}]")
  try:
    yield database
  finally:
    client.close()
    logging.debug("Disconnected from MongoDB")


def init_db(app: MongoDBFastAPI):
  """Attach MongoDB client and DB to the FastAPI app."""
  app.mongodb_client = create_mongo_client()
  app.mongodb = get_mongo_database(app.mongodb_client)
  app.db = Database(app.mongodb)

  logger.info(f"Connected to MongoDB [{settings.MONGO_DB}]")


def close_db(app: MongoDBFastAPI):
  """Cleanly close the MongoDB client."""
  if app.mongodb_client is not None:
    app.mongodb_client.close()
    logging.debug("Disconnected from MongoDB")
