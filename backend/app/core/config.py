import os

from pydantic import BaseModel


class Settings(BaseModel):
    """Runtime settings for the early Madarik API phases."""

    app_name: str = "منصة مدارك"
    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Phase 1-G1: AI provider layer. Mock remains the safe default.
    ai_provider: str = os.getenv("MADARIK_AI_PROVIDER", "mock")
    ai_api_key: str = os.getenv("MADARIK_AI_API_KEY", "")
    ai_model: str = os.getenv("MADARIK_AI_MODEL", "")
    ai_base_url: str = os.getenv("MADARIK_AI_BASE_URL", "https://api.openai.com/v1")
    ai_timeout_seconds: float = float(os.getenv("MADARIK_AI_TIMEOUT_SECONDS", "25"))


settings = Settings()
