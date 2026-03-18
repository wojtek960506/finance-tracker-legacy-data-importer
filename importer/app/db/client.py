from contextlib import asynccontextmanager
from typing import AsyncIterator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from app.db.database import Database
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
