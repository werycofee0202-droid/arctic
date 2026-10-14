from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Удивительная и неизведанная Арктика"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL из settings.json
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "db"

    # JWT
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_super_secret_key_arctic"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней

    # Папки
    UPLOAD_DIR: str = "uploads"
    CERTIFICATE_DIR: str = "certificates"

    # Счётчик участников (для главной страницы)
    FRONTEND_URL: str = "http://localhost:3000"



    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{quote_plus(self.POSTGRES_USER)}:{quote_plus(self.POSTGRES_PASSWORD)}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()