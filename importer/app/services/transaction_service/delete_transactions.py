from bson import ObjectId

from app.db.database import Database

# delete all transactions of a given user
async def delete_transactions(db: Database, ownerId: str) -> int:
  result = await db.transactions.delete_many({ "ownerId": ObjectId(ownerId) })
  return result.deleted_count
