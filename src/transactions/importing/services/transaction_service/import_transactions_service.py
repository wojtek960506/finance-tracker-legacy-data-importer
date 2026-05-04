import json

from src.shared.db.client import database_session
from src.transactions.importing.services.csv_service import prepare_transactions_from_csv
from src.transactions.importing.services.resource_service.create_resource_map import create_resource_map
from src.transactions.importing.services.resource_service.resource_enum import ResourceEnum
from src.transactions.importing.services.user_service import find_user

from .count_transactions import count_transactions
from .create_transactions import create_transactions
from .serialize_object import serialize_object


async def import_transactions(
  owner_id: str,
  csv_file_path: str,
  should_print: bool,
) -> int:
  async with database_session() as db:
    if (await find_user(db, owner_id)) is None:
      print("User not found")
      return 1

    if (await count_transactions(db, owner_id)) > 0:
      print("Cannot import transactions for a user who already has some transactions")
      return 1

    valid_docs, errors = prepare_transactions_from_csv(csv_file_path, owner_id)
    categories_map = await create_resource_map(
      ResourceEnum.CATEGORY, db, owner_id, valid_docs, should_print
    )
    accounts_map = await create_resource_map(
      ResourceEnum.ACCOUNT, db, owner_id, valid_docs, should_print
    )
    payment_methods_map = await create_resource_map(
      ResourceEnum.PAYMENT_METHOD, db, owner_id, valid_docs, should_print
    )

    if errors:
      errors_to_show = list(map(serialize_object, errors[:10]))
      print(json.dumps({
        "valid_transactions_count": len(valid_docs),
        "invalid_transactions_count": len(errors),
        "first_10_errors": errors_to_show,
      }, indent=2, default=str))
      return 1

    print(f"Adding {len(valid_docs)} transactions for user {owner_id}...")
    result = await create_transactions(
      db,
      valid_docs,
      errors,
      categories_map,
      accounts_map,
      payment_methods_map,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0
