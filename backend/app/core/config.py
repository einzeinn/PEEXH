"""Application configuration settings for PEEXH."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    APP_ENV: str = "development"
    APP_NAME: str = "peexh"
    LOG_LEVEL: str = "INFO"

    # AssemblyAI Configuration
    ASSEMBLYAI_API_KEY: Optional[str] = None

    # LLM Provider Configuration
    LLM_PROVIDER: Optional[str] = None
    LLM_MODEL: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None

    # Supabase / Persistence Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    # Deterministic Confidence Policy Thresholds
    PEEXH_HIGH_CONFIDENCE_THRESHOLD: float = 0.80
    PEEXH_LOW_CONFIDENCE_THRESHOLD: float = 0.45
    PEEXH_MIN_STT_CONFIDENCE_FOR_HIGH: float = 0.50

    # Feature Flags
    ENABLE_PERSONAL_MEMORY: bool = True
    ENABLE_TTS: bool = True

    # TTS Configuration
    TTS_PROVIDER: str = "browser"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
