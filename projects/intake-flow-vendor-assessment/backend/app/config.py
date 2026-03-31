from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://ifvuser:ifvpass@localhost:5432/ifvdb"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    local_model: str = "qwen3:14b"

    # CloakLLM
    cloakllm_enabled: bool = True
    cloakllm_spacy_model: str = "en_core_web_sm"

    # SMTP (Postmark — OQ-03 resolved)
    smtp_host: str = "smtp.postmarkapp.com"
    smtp_port: int = 587
    smtp_user: str = "server-api-token"
    smtp_pass: str = ""
    smtp_from: str = "notifications@datadnaprivacy.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()
