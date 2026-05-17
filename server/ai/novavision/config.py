from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from db.config import _find_env_file


class NovaVisionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    novavision_token: str = ""
    novavision_host: str = "alfa.suite.novavision.ai"
    novavision_inference_url: str = "http://localhost:8501"
    novavision_mock: bool = True
    novavision_container_name: str = "novavision"
    novavision_default_app_id: str = "mock-novavision-app"
    novavision_app_port: int = 3030
    novavision_timeout_seconds: float = 30.0
    novavision_ws_channel: str = ""
    novavision_workspace: str = ""
    novavision_service: str = "diginova-wsl"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def live_ready(self) -> bool:
        return bool(self.novavision_token and not self.novavision_mock)


@lru_cache
def get_novavision_settings() -> NovaVisionSettings:
    return NovaVisionSettings()
