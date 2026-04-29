import json

from app.db.client import database_session
from app.services.transaction_service import count_transactions
from app.utils import require_exact_confirmation

from .list_users_utils import count_user_resources


async def delete_all_empty_users() -> dict:
  async with database_session() as db:
    users = await db.users.find({}).sort("_id", 1).to_list(length=None)
    deletable_user_ids = []

    for user in users:
      transactions = await count_transactions(db, str(user["_id"]))
      resources = await count_user_resources(db, user["_id"])

      if transactions == 0 and all(count == 0 for count in resources.values()):
        deletable_user_ids.append(user["_id"])

    users_count = len(deletable_user_ids)
    if users_count == 0:
      return {
        "deleted": False,
        "error": "No users found with zero transactions and zero resources",
        "usersDeleted": 0,
      }

    displayed_confirmation_text = "DELETE ALL EMPTY USERS"
    confirmation_text = f"{displayed_confirmation_text} {users_count}"
    confirmed = require_exact_confirmation(
      confirmation_text,
      "delete all users with zero transactions and zero user-owned resources.\n"
      "Calculate the number of users to delete yourself and append it to the confirmation text, "
      "separated by a space\n"
      f"(users: {users_count})",
      displayed_confirmation_text=displayed_confirmation_text,
    )
    if not confirmed:
      return {
        "deleted": False,
        "error": "Deletion cancelled because confirmation text did not match",
        "usersToDelete": users_count,
      }

    delete_result = await db.users.delete_many({"_id": {"$in": deletable_user_ids}})
    return {
      "deleted": True,
      "usersToDelete": users_count,
      "deletedCount": delete_result.deleted_count,
    }


async def run_delete_all_empty_users() -> int:
  result = await delete_all_empty_users()
  print(json.dumps(result, indent=2, default=str))
  return 0 if result["deleted"] else 1
