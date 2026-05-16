from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> str | None:
    candidates = [
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path.cwd() / ".env",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = ""
    supabase_db_host: str = ""
    supabase_db_name: str = "postgres"
    supabase_db_user: str = "postgres"
    supabase_db_password: str = ""

    environment: str = "development"

    yefai_data_root: str = ""

    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_api_key: str = ""

    # Comma-separated list of platform admin emails
    admin_emails: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def supabase_connected(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_key)


def get_settings() -> Settings:
    return Settings()
