import json

from bson import ObjectId

from src.shared.db.client import database_session
from src.shared.utils import require_exact_confirmation
from src.transactions.importing.services.transaction_service import count_transactions

from .find_user import find_user
from .list_users_utils import count_user_resources


async def delete_user(owner_id: str) -> dict:
  async with database_session() as db:
    user = await find_user(db, owner_id)
    if user is None:
      return {
        "deleted": False,
        "error": "User not found",
        "ownerId": owner_id,
      }

    transactions_count = await count_transactions(db, owner_id)
    resources_count = await count_user_resources(db, ObjectId(owner_id))

    if transactions_count > 0 or any(count > 0 for count in resources_count.values()):
      return {
        "deleted": False,
        "error": "User still owns transactions or resources",
        "ownerId": owner_id,
        "transactions": transactions_count,
        **resources_count,
      }

    user_label = user.get("email") or owner_id
    confirmed = require_exact_confirmation(
      "DELETE USER",
      f"delete user with email {user_label}",
    )
    if not confirmed:
      return {
        "deleted": False,
        "error": "Deletion cancelled because confirmation text did not match",
        "ownerId": owner_id,
      }

    delete_result = await db.users.delete_one({"_id": ObjectId(owner_id)})
    return {
      "deleted": delete_result.deleted_count == 1,
      "ownerId": owner_id,
      "deletedCount": delete_result.deleted_count,
    }


async def run_delete_user(owner_id: str) -> int:
  result = await delete_user(owner_id)
  print(json.dumps(result, indent=2, default=str))
  return 0 if result["deleted"] else 1
