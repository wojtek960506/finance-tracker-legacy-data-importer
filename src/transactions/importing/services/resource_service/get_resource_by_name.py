from bson import ObjectId

from src.shared.db.database import Database
from src.shared.utils import normalize_whitespace

from .resource_enum import ResourceEnum


async def get_resource_by_name(
  resource_enum: ResourceEnum,
  db: Database,
  name: str,
  owner_id: str,
):
  return await db.collection(resource_enum).find_one({
    "nameNormalized": normalize_whitespace(name).lower(),
    "$or": [
      { "type": "user", "ownerId": ObjectId(owner_id) },
      { "type": "system", "ownerId": None },
    ]
  })
