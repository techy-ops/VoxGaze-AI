import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Locate backend directory and load .env file if available
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()


class Settings(BaseSettings):
    """
    Application Settings configuration loaded from environment variables.
    """
    APP_NAME: str = "VoxGaze AI Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SECRET_KEY: str = "supersecretkey_change_in_production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "*"]

    DATABASE_URL: str = "sqlite+aiosqlite:///./voxgaze.db"

    # Firebase Admin SDK Configuration
    FIREBASE_PROJECT_ID: str = "voxgaze-ai-dev"
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_STORAGE_BUCKET: str = "voxgaze-ai-dev.appspot.com"
    FIREBASE_DATABASE_URL: str = "https://voxgaze-ai-dev-default-rtdb.firebaseio.com"
    FIREBASE_CREDENTIALS_PATH: str = "./firebase_credentials.json"

    # JWT Authentication Configuration
    JWT_SECRET: str = "supersecret_jwt_key_change_in_prod_voxgaze"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Third-party integrations
    OPENAI_API_KEY: str = "mock_openai_api_key"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
