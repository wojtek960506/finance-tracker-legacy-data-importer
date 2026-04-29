from bson import ObjectId
from app.db.database import Database

async def count_transactions(db: Database, owner_id: str):
  return await db.transactions.count_documents({"ownerId": ObjectId(owner_id)})
