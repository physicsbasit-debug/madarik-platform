import os
from pathlib import Path

from pydantic import BaseModel


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = BACKEND_ROOT / "data"


class Settings(BaseModel):
    """Runtime settings for the Madarik API."""

    app_name: str = "منصة مدارك"
    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Phase 2-A1: SQLite persistence foundation.
    data_dir: str = os.getenv("MADARIK_DATA_DIR", str(DEFAULT_DATA_DIR))
    db_path: str = os.getenv("MADARIK_DB_PATH", str(DEFAULT_DATA_DIR / "madarik.sqlite3"))

    # Phase 1-G1: AI provider layer. Mock remains the safe default.
    ai_provider: str = os.getenv("MADARIK_AI_PROVIDER", "mock")
    ai_api_key: str = os.getenv("MADARIK_AI_API_KEY", "")
    ai_model: str = os.getenv("MADARIK_AI_MODEL", "")
    ai_base_url: str = os.getenv("MADARIK_AI_BASE_URL", "https://api.openai.com/v1")
    ai_timeout_seconds: float = float(os.getenv("MADARIK_AI_TIMEOUT_SECONDS", "25"))
    ai_max_input_chars: int = int(os.getenv("MADARIK_AI_MAX_INPUT_CHARS", "2400"))
    ai_temperature: float = float(os.getenv("MADARIK_AI_TEMPERATURE", "0.1"))
    ai_external_enabled: bool = os.getenv("MADARIK_AI_EXTERNAL_ENABLED", "true").lower() in {"1", "true", "yes", "on"}


settings = Settings()
