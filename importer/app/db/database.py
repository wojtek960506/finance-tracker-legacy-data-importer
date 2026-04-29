from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from app.services.resource_service.resource_enum import ResourceEnum


class Database:
  def __init__(self, db: AsyncIOMotorDatabase):
    self._db = db
    self.users: AsyncIOMotorCollection = db.users
    self.transactions: AsyncIOMotorCollection = db.transactions
    self.counters: AsyncIOMotorCollection = db.counters

  def collection(self, resource: ResourceEnum) -> AsyncIOMotorCollection:
    return getattr(self._db, resource.collection_name)
