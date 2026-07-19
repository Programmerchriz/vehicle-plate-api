from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DATABASE_URL: str

    UPLOAD_DIR: str
    STATIC_DIR: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    YOLO_MODEL_PATH: str = "app/ai/models/license_plate.pt"
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024
    PLATE_IMAGE_WIDTH: int = 1000
    # PLATE_IMAGE_HEIGHT: int = 200
    DETECTION_CONFIDENCE_THRESHOLD: float = 0.55
    OCR_CONFIDENCE_THRESHOLD: float = 0.40


settings = Settings()