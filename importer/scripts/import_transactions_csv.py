import argparse
import asyncio
from app.services.admin_guard import require_admin_auth
from app.services.transaction_service import import_transactions


def main():
  parser = argparse.ArgumentParser(
    description="Import transactions from CSV without running the API server.",
  )
  parser.add_argument("owner_id", help="Mongo ObjectId of the user passed as a string")
  parser.add_argument("csv_path", help="Path to CSV file")
  parser.add_argument(
    "--print",
    action="store_true",
    help="Print resource lookup and creation logs during import.",
  )
  args = parser.parse_args()

  require_admin_auth()
  exit_code = asyncio.run(
    import_transactions(args.owner_id, args.csv_path, args.print)
  )
  raise SystemExit(exit_code)


if __name__ == "__main__":
  main()
