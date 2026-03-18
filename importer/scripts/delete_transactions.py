import argparse
import asyncio
import json

from app.db.client import database_session
from app.services.transaction_service import delete_transactions


async def run_transactions_deletion(owner_id: str) -> int:
  async with database_session() as db:
    deleted_count = await delete_transactions(db, owner_id)
    print(json.dumps({ "deletedCount": deleted_count }, indent=2, default=str))
    return 0
  
def main():
  parser = argparse.ArgumentParser(
    description="Delete all transactions of a given user",
  )
  parser.add_argument("owner_id", help="Mongo ObjectId of the user passed as a string")
  args = parser.parse_args()

  exit_code = asyncio.run(run_transactions_deletion(args.owner_id))
  raise SystemExit(exit_code)

if __name__ == "__main__":
  main()
