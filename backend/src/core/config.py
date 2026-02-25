from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Oculus Feldsher API"
    ENV: str = "dev"

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    DATABASE_URL: str = "sqlite:///./oculus.db"

    JWT_SECRET: str = "46RNH65hFHH6SD8g67GHD89gm3684rgDY80w7ry2098Y2"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    @property
    def cors_origins_list(self) -> List[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]

settings = Settings()