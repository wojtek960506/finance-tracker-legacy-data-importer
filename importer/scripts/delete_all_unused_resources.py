import argparse
import asyncio

from app.services.admin_guard import require_admin_auth
from app.services.user_service import run_delete_all_unused_resources


def main():
  parser = argparse.ArgumentParser(
    description=(
      "Delete all user-owned named resources for users who have no transactions."
    ),
  )
  parser.parse_args()

  require_admin_auth()
  exit_code = asyncio.run(run_delete_all_unused_resources())
  raise SystemExit(exit_code)


if __name__ == "__main__":
  main()
