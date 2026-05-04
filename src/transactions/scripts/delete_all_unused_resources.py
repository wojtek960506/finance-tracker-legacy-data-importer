import argparse
import asyncio

from src.transactions.importing.services.admin_guard import AdminAuthError, require_admin_auth
from src.transactions.importing.services.user_service import run_delete_all_unused_resources


def main():
  parser = argparse.ArgumentParser(
    description=(
      "Delete all user-owned named resources for users who have no transactions."
    ),
  )
  parser.parse_args()

  try:
    require_admin_auth()
  except AdminAuthError as err:
    print(str(err))
    raise SystemExit(1)

  exit_code = asyncio.run(run_delete_all_unused_resources())
  raise SystemExit(exit_code)


if __name__ == "__main__":
  main()
