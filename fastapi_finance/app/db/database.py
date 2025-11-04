from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

class Database:
  def __init__(self, db: AsyncIOMotorDatabase):
    self._db = db
    self.transactions: AsyncIOMotorCollection = db.transactions
