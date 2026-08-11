from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ORX Core"
    app_version: str = "0.2.0"
    environment: str = "development"

    currency_name: str = "ORX"
    currency_code: str = "ORX"
    currency_network: str = "ORLIX"

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/orx"
    )
    redis_url: str = "redis://localhost:6379/0"

    admin_api_key: str = "change-me-in-production"
    treasury_external_id: str = "ORX_TREASURY"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
