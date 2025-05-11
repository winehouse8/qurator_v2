import os, yaml
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()               # .env 로드

class Settings(BaseSettings):
    mongo_uri: str = Field(..., env="MONGO_URI")
    api_hash_secret: str = Field(..., env="API_HASH_SECRET")  # HMAC용

    proxy_host: str | None = Field(None, env="PROXY_HOST")
    proxy_user: str | None = Field(None, env="PROXY_USER")
    proxy_pass: str | None = Field(None, env="PROXY_PASS")
    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")

    worker_count: int | None = 1

    rate_limit_per_min: int = 60    # 기본 60rpm
    cors_origins: list[str] = []

    # Proxy & 기타 YAML 설정 병합
    ports: list[int] = []
    min_delay: int = 10
    max_retries: int = 2


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 

def load_settings() -> Settings:
    cfg = {}
    if os.path.exists("config.yaml"):
        with open("config.yaml", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    return Settings(**cfg)

@lru_cache
def get_settings() -> Settings:
    return load_settings()
