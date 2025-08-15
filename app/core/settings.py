from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # app
    APP_NAME: str = "Minha API"
    ENVIRONMENT: str = "dev"

    # banco
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@db:5432/appdb"

    # CORS
    ALLOWED_ORIGINS: str = "*"

    def allowed_origins_list(self) -> List[str]:
        raw = self.ALLOWED_ORIGINS
        if raw.strip() == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
