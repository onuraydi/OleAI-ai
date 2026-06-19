from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "OleAI AI Engine"
    API_V1_STR: str = "/api/v1"
    
    # Security
    AI_SERVICE_API_KEY: str = "oleai_shared_secret_key_for_development"
    ALLOWED_HOSTS: List[str] = ["*"]

    # ML Model Config
    MODEL_MAX_FEATURES: int = 10000
    DECAY_CONSTANT: float = 0.0231 # 30 day half-life
    
    # Integration
    BACKEND_URL: str = "https://localhost:7190"
    BACKEND_SYNC_URL: str = ""
    VERIFY_SSL: bool = False

    from pydantic import model_validator
    @model_validator(mode='after')
    def _build_sync_url(self) -> 'Settings':
        if not self.BACKEND_SYNC_URL:
            self.BACKEND_SYNC_URL = f"{self.BACKEND_URL}/api/recipes/ai-sync"
        return self

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: str = "60"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()

