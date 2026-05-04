import argparse
import asyncio

from src.transactions.importing.services.admin_guard import AdminAuthError, require_admin_auth
from src.transactions.importing.services.transaction_service import run_delete_transactions
  
def main():
  parser = argparse.ArgumentParser(
    description="Delete all transactions of a given user",
  )
  parser.add_argument("owner_id", help="Mongo ObjectId of the user passed as a string")
  args = parser.parse_args()

  try:
    require_admin_auth()
  except AdminAuthError as err:
    print(str(err))
    raise SystemExit(1)

  exit_code = asyncio.run(run_delete_transactions(args.owner_id))
  raise SystemExit(exit_code)

if __name__ == "__main__":
  main()
