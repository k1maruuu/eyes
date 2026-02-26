from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Oculus Feldsher API"
    ENV: str = "dev"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    DATABASE_URL: str
    DB_SSLMODE: str = "prefer"   # prefer | require | verify-full

    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    @property
    def cors_origins_list(self) -> List[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]

settings = Settings()