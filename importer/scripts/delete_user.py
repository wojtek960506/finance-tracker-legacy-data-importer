import argparse
import asyncio

from app.services.admin_guard import require_admin_auth
from app.services.user_service import run_delete_user


def main():
  parser = argparse.ArgumentParser(
    description="Delete a user who has no transactions and no user-owned resources.",
  )
  parser.add_argument("owner_id", help="Mongo ObjectId of the user passed as a string")
  args = parser.parse_args()

  require_admin_auth()
  exit_code = asyncio.run(run_delete_user(args.owner_id))
  raise SystemExit(exit_code)


if __name__ == "__main__":
  main()
