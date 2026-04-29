import json

from app.db.client import database_session
from app.services.transaction_service import count_transactions
from app.utils import require_exact_confirmation

from .list_users_utils import RESOURCE_COLLECTIONS


async def delete_all_unused_resources() -> dict:
  async with database_session() as db:
    users = await db.users.find({}).sort("_id", 1).to_list(length=None)
    owner_ids_without_transactions = []

    for user in users:
      transactions = await count_transactions(db, str(user["_id"]))
      if transactions == 0:
        owner_ids_without_transactions.append(user["_id"])

    counts = {}
    for output_name, resource_enum in RESOURCE_COLLECTIONS.items():
      counts[output_name] = await db.collection(resource_enum).count_documents({
        "ownerId": {"$in": owner_ids_without_transactions},
        "type": "user",
      })

    total_resources = sum(counts.values())
    if total_resources == 0:
      return {
        "deleted": False,
        "error": "No unused resources found for users without transactions",
        "usersWithoutTransactions": len(owner_ids_without_transactions),
        **counts,
      }

    displayed_confirmation_text = "DELETE ALL UNUSED RESOURCES"
    confirmation_text = f"{displayed_confirmation_text} {total_resources}"
    confirmed = require_exact_confirmation(
      confirmation_text,
      "delete all unused named resources for users with no transactions.\n"
      "Calculate the sum of the following counts yourself "
      "and append it to the confirmation text, separated by a space\n"
      f"(accounts: {counts['accounts']}, categories: {counts['categories']}, "
      f"paymentMethods: {counts['paymentMethods']})",
      displayed_confirmation_text=displayed_confirmation_text,
    )
    if not confirmed:
      return {
        "deleted": False,
        "error": "Deletion cancelled because confirmation text did not match",
        "usersWithoutTransactions": len(owner_ids_without_transactions),
        **counts,
      }

    deleted_counts = {}
    for output_name, resource_enum in RESOURCE_COLLECTIONS.items():
      result = await db.collection(resource_enum).delete_many({
        "ownerId": {"$in": owner_ids_without_transactions},
        "type": "user",
      })
      deleted_counts[output_name] = result.deleted_count

    return {
      "deleted": True,
      "usersWithoutTransactions": len(owner_ids_without_transactions),
      "deletedCounts": deleted_counts,
      "totalDeleted": sum(deleted_counts.values()),
    }


async def run_delete_all_unused_resources() -> int:
  result = await delete_all_unused_resources()
  print(json.dumps(result, indent=2, default=str))
  return 0 if result["deleted"] else 1
