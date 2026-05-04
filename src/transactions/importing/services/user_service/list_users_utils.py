from bson import ObjectId

from src.transactions.importing.services.resource_service.resource_enum import ResourceEnum


RESOURCE_COLLECTIONS = {
  "accounts": ResourceEnum.ACCOUNT,
  "categories": ResourceEnum.CATEGORY,
  "paymentMethods": ResourceEnum.PAYMENT_METHOD,
}

USER_FIELDS = [
  "email",
  "name",
  "displayName",
  "username",
]


def serialize_value(value):
  if isinstance(value, ObjectId):
    return str(value)
  if isinstance(value, list):
    return [serialize_value(item) for item in value]
  if isinstance(value, dict):
    return {key: serialize_value(item) for key, item in value.items()}
  return value


async def count_user_resources(db, owner_id: ObjectId) -> dict[str, int]:
  result = {}

  for output_name, resource_enum in RESOURCE_COLLECTIONS.items():
    result[output_name] = await db.collection(resource_enum).count_documents({
      "ownerId": owner_id,
      "type": "user",
    })

  return result


def serialize_user(user: dict, counts: dict[str, int]) -> dict:
  result = {
    "_id": str(user["_id"]),
    **counts,
  }

  for field in USER_FIELDS:
    if field in user:
      result[field] = serialize_value(user[field])

  return result
