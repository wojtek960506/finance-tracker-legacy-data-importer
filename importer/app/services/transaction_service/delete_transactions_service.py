import json

from app.db.client import database_session
from app.services.user_service import find_user
from app.utils import require_exact_confirmation

from .delete_transactions import delete_transactions


async def delete_transactions_for_user(owner_id: str) -> dict:
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
      "DELETE TRANSACTIONS",
      f"delete all transactions of user with email {user_label}",
    )
    if not confirmed:
      return {
        "deleted": False,
        "error": "Deletion cancelled because confirmation text did not match",
        "ownerId": owner_id,
      }

    deleted_count = await delete_transactions(db, owner_id)
    return {
      "deleted": True,
      "ownerId": owner_id,
      "deletedCount": deleted_count,
    }


async def run_delete_transactions(owner_id: str) -> int:
  result = await delete_transactions_for_user(owner_id)
  print(json.dumps(result, indent=2, default=str))
  return 0 if result["deleted"] else 1
