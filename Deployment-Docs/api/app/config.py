from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path



class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",
                                      extra="ignore")

    app_name: str
    service_name: str
    environment: str
    log_level: str
    api_v1_prefix: str
    api_v2_prefix: str
    secret_key: SecretStr | None = None
    data_source_mode: str
    master_data_directory: Path
    service_base_url: str
    service_timeout_seconds: float
    gateway_auth_enabled: bool
    gateway_api_key: SecretStr | None = None
    gateway_rate_limit: int = 60
    gateway_rate_window_seconds: int = 60

settings = Settings()


