from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


IMPORTING_DIR = Path(__file__).resolve().parents[2] / "transactions" / "importing"

class Settings(BaseSettings):
  MONGO_URI: str
  MONGO_DB: str
  LEGACY_IMPORTER_ADMIN_TOKEN: Optional[str] = None

  model_config = ConfigDict(env_file=IMPORTING_DIR / ".env")


settings = Settings()
