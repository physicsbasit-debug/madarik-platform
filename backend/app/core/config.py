import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = BACKEND_ROOT / "data"

# Local development convenience. Real environment variables and Codespaces
# secrets keep priority because override=False.
load_dotenv(BACKEND_ROOT / ".env", override=False)


class Settings(BaseModel):
    """Runtime settings for the Madarik API."""

    app_name: str = "منصة مدارك"
    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Phase 2-A1: SQLite persistence foundation.
    data_dir: str = os.getenv("MADARIK_DATA_DIR", str(DEFAULT_DATA_DIR))
    db_path: str = os.getenv("MADARIK_DB_PATH", str(DEFAULT_DATA_DIR / "madarik.sqlite3"))

    # Phase 4-A1: real scientific translation provider.
    # Mock remains the safe default; external calls require explicit enablement.
    ai_provider: str = os.getenv("MADARIK_AI_PROVIDER", "mock")
    ai_api_key: str = os.getenv("MADARIK_AI_API_KEY", "")
    ai_model: str = os.getenv("MADARIK_AI_MODEL", "")
    ai_base_url: str = os.getenv("MADARIK_AI_BASE_URL", "https://api.openai.com/v1")

    # Phase 4-A2b: Gemini provider settings. Dedicated Gemini variables are
    # preferred when Gemini is selected, while the generic Phase 4-A1 settings
    # remain available for OpenAI and OpenAI-compatible providers.
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "")
    gemini_base_url: str = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta",
    )

    ai_timeout_seconds: float = float(os.getenv("MADARIK_AI_TIMEOUT_SECONDS", "45"))
    ai_max_input_chars: int = int(os.getenv("MADARIK_AI_MAX_INPUT_CHARS", "4000"))
    ai_max_output_tokens: int = int(os.getenv("MADARIK_AI_MAX_OUTPUT_TOKENS", "1200"))
    ai_temperature: float = float(os.getenv("MADARIK_AI_TEMPERATURE", "0.1"))
    ai_external_enabled: bool = os.getenv("MADARIK_AI_EXTERNAL_ENABLED", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


    # Phase 3-A: Google Drive source foundation.
    google_drive_provider: str = os.getenv(
        "MADARIK_GOOGLE_DRIVE_PROVIDER",
        "disabled",
    )
    google_drive_access_token: str = os.getenv(
        "MADARIK_GOOGLE_DRIVE_ACCESS_TOKEN",
        "",
    )
    google_drive_folder_id: str = os.getenv(
        "MADARIK_GOOGLE_DRIVE_FOLDER_ID",
        "",
    )
    google_drive_timeout_seconds: float = float(
        os.getenv("MADARIK_GOOGLE_DRIVE_TIMEOUT_SECONDS", "30")
    )


settings = Settings()
