from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    GCP_STORAGE_BUCKET_NAME: str = "images"
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None  # Optional: path to service account key file

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()