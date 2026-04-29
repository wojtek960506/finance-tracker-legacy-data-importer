from bson import ObjectId
from app.db.database import Database

async def find_user(db: Database, id: str):
  return await db.users.find_one({"_id": ObjectId(id)})
