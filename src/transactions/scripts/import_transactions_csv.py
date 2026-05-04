import argparse
import asyncio
from src.transactions.importing.services.admin_guard import AdminAuthError, require_admin_auth
from src.transactions.importing.services.transaction_service import import_transactions


def main():
  parser = argparse.ArgumentParser(
    description="Import transactions from CSV through the local admin and migration CLI.",
  )
  parser.add_argument("owner_id", help="Mongo ObjectId of the user passed as a string")
  parser.add_argument("csv_path", help="Path to CSV file")
  parser.add_argument(
    "--print",
    action="store_true",
    help="Print resource lookup and creation logs during import.",
  )
  args = parser.parse_args()

  try:
    require_admin_auth()
  except AdminAuthError as err:
    print(str(err))
    raise SystemExit(1)

  exit_code = asyncio.run(
    import_transactions(args.owner_id, args.csv_path, args.print)
  )
  raise SystemExit(exit_code)


if __name__ == "__main__":
  main()
