import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema Parroquia SMV"
    API_V1_STR: str = "/api/v1"

    # Variable clave para producción. FastAPI la leerá de tu .env
    DATABASE_URL: Optional[str] = None

    # Variables locales por si falla la nube (tu respaldo local)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "250804post"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "db_parroquia_sjmv"

    SQLALCHEMY_DATABASE_URI: str = ""

    SECRET_KEY: str = "CAMBIAME_EN_PRODUCCION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **values):
        super().__init__(**values)
        # Lógica inteligente: Si hay URL de Supabase, úsala. Si no, arma la local.
        if self.DATABASE_URL:
            self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
        else:
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}:"
                f"{self.POSTGRES_PORT}/"
                f"{self.POSTGRES_DB}"
            )

settings = Settings()