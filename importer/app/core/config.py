from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
  MONGO_URI: str
  MONGO_DB: str
  LEGACY_IMPORTER_ADMIN_TOKEN: Optional[str] = None

  model_config = ConfigDict(env_file=".env")


settings = Settings()
