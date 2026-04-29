from getpass import getpass
from secrets import compare_digest

from app.core.config import settings


def require_admin_auth() -> None:
  expected_token = settings.LEGACY_IMPORTER_ADMIN_TOKEN

  if expected_token is None or expected_token.strip() == "":
    raise RuntimeError(
      "LEGACY_IMPORTER_ADMIN_TOKEN has to be set in importer/.env before using "
      "legacy importer mutation scripts"
    )

  provided_token = getpass("Legacy importer admin token: ")

  if not compare_digest(provided_token, expected_token):
    raise PermissionError("Invalid legacy importer admin token")
