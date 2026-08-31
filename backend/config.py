import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    RAZORPAY_KEY_ID: str = "rzp_test_dummy"
    RAZORPAY_KEY_SECRET: str = "dummy_secret"
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Path relative to project root or absolute
    DATABASE_URL: str = "sqlite:///data/recoverai.db"
    
    LOG_LEVEL: str = "INFO"
    MAX_RETRIES: int = 3
    RETRY_COOLDOWN_HOURS: int = 24
    NUDGE_QUIET_START: int = 21
    NUDGE_QUIET_END: int = 8

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
