from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
  MONGO_URI: str
  MONGO_DB: str

  model_config = ConfigDict(env_file=".env")


settings = Settings()
