from bson import ObjectId
from app.db.database import Database

async def count_transactions(db: Database, owner_id: str):
  return db.transactions.count_documents({"ownerId": ObjectId(owner_id)})
