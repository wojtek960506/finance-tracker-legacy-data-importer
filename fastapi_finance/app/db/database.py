from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

class Database:
  def __init__(self, db: AsyncIOMotorDatabase):
    self._db = db
    self.users: AsyncIOMotorCollection = db.users
    self.transactions: AsyncIOMotorCollection = db.transactions
    self.counters: AsyncIOMotorCollection = db.counters
    self.categories: AsyncIOMotorCollection = db.categories
