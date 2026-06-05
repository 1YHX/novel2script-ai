from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'novel2script.db'}"
    use_mock_llm: bool = True
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
