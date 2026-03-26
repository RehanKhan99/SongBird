import os
from enum import StrEnum

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentOption(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # app
    APP_NAME: str = "SongBird InsurTech"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: EnvironmentOption = EnvironmentOption.LOCAL
    LOG_LEVEL: str = "INFO"

    # auth
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # db
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def POSTGRES_ASYNC_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis
    REDIS_URL: str

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # sudo
    ADMIN_NAME: str
    ADMIN_EMAIL: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    # empty for fallback mock
    OWM_API_KEY: str = ""
    OPENAQ_API_KEY: str = ""
    HERE_API_KEY: str = ""
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"

    # twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = ""
    TWILIO_WHATSAPP_TO: str = ""

    MOCK_OTP: str = "123456"

settings = Settings()  # type: ignore[call-arg]
