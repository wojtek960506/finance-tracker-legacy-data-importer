import argparse
import asyncio

from app.services.admin_guard import require_admin_auth
from app.services.transaction_service import run_delete_transactions
  
def main():
  parser = argparse.ArgumentParser(
    description="Delete all transactions of a given user",
  )
  parser.add_argument("owner_id", help="Mongo ObjectId of the user passed as a string")
  args = parser.parse_args()

  require_admin_auth()
  exit_code = asyncio.run(run_delete_transactions(args.owner_id))
  raise SystemExit(exit_code)

if __name__ == "__main__":
  main()
