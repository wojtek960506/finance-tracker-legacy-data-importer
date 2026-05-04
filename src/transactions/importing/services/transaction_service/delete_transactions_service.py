import json

from src.shared.db.client import database_session
from src.shared.utils import require_exact_confirmation
from src.transactions.importing.services.user_service import find_user

from .count_transactions import count_transactions
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
    transactions_count = await count_transactions(db, owner_id)
    displayed_confirmation_text = "DELETE TRANSACTIONS"
    confirmation_text = f"{displayed_confirmation_text} {transactions_count}"
    confirmed = require_exact_confirmation(
      confirmation_text,
      "delete all transactions of user with email "
      f"{user_label}.\n"
      "Calculate the number of transactions yourself and append it to the confirmation text, "
      "separated by a space\n"
      f"(transactions: {transactions_count})",
      displayed_confirmation_text=displayed_confirmation_text,
    )
    if not confirmed:
      return {
        "deleted": False,
        "error": "Deletion cancelled because confirmation text did not match",
        "ownerId": owner_id,
        "transactions": transactions_count,
      }

    print(f"Deleting all transactions for user {owner_id}...")
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
