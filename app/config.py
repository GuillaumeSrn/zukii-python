from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Configuration du micro-service d'analyse IA"""
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.3
    jwt_secret: str = "zukii-python-secret-key-2024"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    anonymization_enabled: bool = True
    data_retention_days: int = 30
    max_file_size_mb: int = 50
    max_analysis_timeout: int = 300
    max_concurrent_analyses: int = 10
    log_level: str = "INFO"
    log_file: str = "logs/analysis_service.log"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    cors_origins: list = ["http://localhost:3000", "http://localhost:4200"]

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

settings = Settings() 