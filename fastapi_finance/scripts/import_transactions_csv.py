import argparse
import asyncio
import json
from bson import ObjectId
from app.db.client import database_session
from app.services.category_service import create_categories_map
from app.services.csv_service import prepare_transactions_from_csv_path
from app.services.transaction_service import (
  create_many_transactions,
  serialize_object_id_if_any,
)


async def run_import(owner_id: str, csv_path: str) -> int:
  async with database_session() as db:
    if (await db.users.find_one({"_id": ObjectId(owner_id)})) is None:
      print("User not found")
      return 1

    if (await db.transactions.count_documents({"ownerId": ObjectId(owner_id)})) > 0:
      print("Cannot import transactions for a user who already has some transactions")
      return 1

    valid_docs, errors = prepare_transactions_from_csv_path(csv_path, owner_id)
    categories_map = await create_categories_map(db, owner_id, valid_docs)

    if errors:
      errors_to_show = list(map(serialize_object_id_if_any, errors[:10]))
      print(json.dumps({
        "valid_transactions_count": len(valid_docs),
        "invalid_transactions_count": len(errors),
        "first_10_errors": errors_to_show,
      }, indent=2, default=str))
      return 1

    result = await create_many_transactions(db, valid_docs, errors, categories_map)
    print(json.dumps(result, indent=2, default=str))
    return 0


def main():
  parser = argparse.ArgumentParser(
    description="Import transactions from CSV without running the API server.",
  )
  parser.add_argument("owner_id", help="Mongo ObjectId of the user")
  parser.add_argument("csv_path", help="Path to CSV file")
  args = parser.parse_args()

  exit_code = asyncio.run(run_import(args.owner_id, args.csv_path))
  raise SystemExit(exit_code)


if __name__ == "__main__":
  main()
