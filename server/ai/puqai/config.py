from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from db.config import _find_env_file


class PuqAISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    puqai_anomaly_webhook: str = ""
    puqai_email_webhook: str = ""
    puqai_sms_webhook: str = ""
    puqai_spare_parts_webhook: str = ""
    puqai_po_webhook: str = ""
    puqai_fallback_enabled: bool = True
    puqai_retry_max_attempts: int = 3
    puqai_retry_backoff_base: float = 1.0
    puqai_request_timeout: float = 10.0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def configured(self) -> bool:
        return bool(self.puqai_anomaly_webhook)

    @property
    def webhook_map(self) -> dict[str, str]:
        return {
            "anomaly": self.puqai_anomaly_webhook,
            "email": self.puqai_email_webhook,
            "sms": self.puqai_sms_webhook,
            "spare_parts": self.puqai_spare_parts_webhook,
            "po": self.puqai_po_webhook,
        }


@lru_cache
def get_puqai_settings() -> PuqAISettings:
    return PuqAISettings()
