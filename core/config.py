from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    # Origins allowed to call this API from a browser. The frontend dev
    # server needs to be listed explicitly because credentialed CORS
    # requests (the refresh cookie) forbid a wildcard origin.
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    


settings = Settings()