from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    GCP_STORAGE_BUCKET_NAME: str = "images"
    GCP_PROJECT_ID: str | None = None
    GCP_CREDENTIALS_PATH: str | None = None
    DETECTION_API_URL: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()