import json

from app.db.client import database_session
from app.utils import print_table

from .list_users_utils import RESOURCE_COLLECTIONS, serialize_value


def serialize_resource(resource_type: str, resource: dict) -> dict:
  return {
    "resourceType": resource_type,
    "_id": serialize_value(resource.get("_id")),
    "name": serialize_value(resource.get("name")),
    "type": serialize_value(resource.get("type")),
    "ownerId": serialize_value(resource.get("ownerId")),
  }


async def run_ownerless_resources_list(as_json: bool) -> int:
  async with database_session() as db:
    print("Checking user-owned resources for missing owners...")

    result = []

    for output_name, resource_enum in RESOURCE_COLLECTIONS.items():
      resources = await db.collection(resource_enum).find({
        "type": "user",
        "$or": [
          {"ownerId": {"$exists": False}},
          {"ownerId": None},
        ],
      }).sort("_id", 1).to_list(length=None)

      for resource in resources:
        result.append(serialize_resource(output_name, resource))

    if as_json:
      print(json.dumps(result, indent=2, default=str))
    else:
      print_table(result)

    return 0
