import json

from bson import ObjectId

from src.shared.db.client import database_session
from src.shared.utils import require_exact_confirmation
from src.transactions.importing.services.resource_service.resource_enum import ResourceEnum

from .find_user import find_user


RESOURCE_USAGE_FIELDS = {
  "accounts": ("accountId", ResourceEnum.ACCOUNT),
  "categories": ("categoryId", ResourceEnum.CATEGORY),
  "paymentMethods": ("paymentMethodId", ResourceEnum.PAYMENT_METHOD),
}


async def delete_unused_resources_for_user(owner_id: str) -> dict:
  async with database_session() as db:
    user = await find_user(db, owner_id)
    if user is None:
      return {
        "deleted": False,
        "error": "User not found",
        "ownerId": owner_id,
      }

    user_label = user.get("email") or owner_id
    confirmed = require_exact_confirmation(
      "DELETE RESOURCES",
      f"delete unused named resources of user with email {user_label}",
    )
    if not confirmed:
      return {
        "deleted": False,
        "error": "Deletion cancelled because confirmation text did not match",
        "ownerId": owner_id,
      }

    owner_object_id = ObjectId(owner_id)
    deleted_counts = {}
    kept_counts = {}

    for output_name, (transaction_field, resource_enum) in RESOURCE_USAGE_FIELDS.items():
      used_resource_ids = await db.transactions.distinct(
        transaction_field,
        {"ownerId": owner_object_id},
      )

      deleted_result = await db.collection(resource_enum).delete_many({
        "ownerId": owner_object_id,
        "type": "user",
        "_id": {"$nin": used_resource_ids},
      })

      remaining_count = await db.collection(resource_enum).count_documents({
        "ownerId": owner_object_id,
        "type": "user",
      })

      deleted_counts[output_name] = deleted_result.deleted_count
      kept_counts[output_name] = remaining_count

    return {
      "deleted": True,
      "ownerId": owner_id,
      "deletedCounts": deleted_counts,
      "keptCounts": kept_counts,
    }


async def run_delete_resources(owner_id: str) -> int:
  result = await delete_unused_resources_for_user(owner_id)
  print(json.dumps(result, indent=2, default=str))
  return 0 if result["deleted"] else 1
