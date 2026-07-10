from pydantic import BaseModel


class Settings(BaseModel):
    """Runtime settings for the early Madarik API phases."""

    app_name: str = "منصة مدارك"
    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
