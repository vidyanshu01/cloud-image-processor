from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.logging import logger


logger.info("Loading application settings")


class Settings(BaseSettings):

    # Application
    APP_NAME: str = "Cloud Image Processing Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Image
    MAX_FILE_SIZE_MB: int = 10

    # AWS S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-south-1"
    AWS_S3_BUCKET_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


logger.info(
    "Application settings loaded successfully"
)