from bson import ObjectId
from app.db.database import Database
from app.utils import normalize_whitespace
from .resource_enum import ResourceEnum


async def create_resource(
  resource_enum: ResourceEnum,
  db: Database,
  name: str,
  owner_id: str,
):
  if owner_id is None:
    raise ValueError(
      detail=f"You can only create user {resource_enum.field_name} so owner has to be specified"
    )
  
  doc = {
    "ownerId": ObjectId(owner_id),
    "type": "user",
    "name": normalize_whitespace(name),
    "nameNormalized": normalize_whitespace(name).lower(),
  }
  result = await db.collection(resource_enum).insert_one(doc)

  print(f"inserted {resource_enum.field_name} result:", result)

  doc_with_id = dict(doc)
  doc_with_id["_id"] = result.inserted_id
  return doc_with_id
