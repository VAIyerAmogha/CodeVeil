from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongodb_url: str = ""
    mongodb_db_name: str = "codeveil"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    groq_api_key: str = ""
    groq_api_keys: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    enable_enrichment: bool = False
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60


settings = Settings()