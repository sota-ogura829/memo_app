from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Memo App API"
    DATABASE_URL: str
    SECRET_KEY: str
    ENCRYPTION_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    APP_ENV: str = "development"
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(case_sensitive=False)

    @property
    def cors_origins(self) -> list[str]:
        return [
            "http://localhost",
            "http://127.0.0.1",
            "http://localhost:80",
            "http://127.0.0.1:80",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]


settings = Settings()
