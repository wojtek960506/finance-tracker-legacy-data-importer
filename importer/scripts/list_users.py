import argparse
import asyncio

from app.services.admin_guard import AdminAuthError, require_admin_auth
from app.services.user_service import run_users_list


def main():
  parser = argparse.ArgumentParser(
    description="List users with transaction counts.",
  )
  parser.add_argument(
    "--include-raw",
    action="store_true",
    help="Include all user document fields in the JSON output.",
  )
  parser.add_argument(
    "--json",
    action="store_true",
    help="Print the output as JSON instead of a table.",
  )
  args = parser.parse_args()

  try:
    require_admin_auth()
  except AdminAuthError as err:
    print(str(err))
    raise SystemExit(1)

  exit_code = asyncio.run(run_users_list(args.include_raw, args.json))
  raise SystemExit(exit_code)


if __name__ == "__main__":
  main()
