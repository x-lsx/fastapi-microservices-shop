from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    app_name: str = Field("FastAPI Shop", alias="APP_NAME")
    debug: bool = Field(False, alias="DEBUG")

    db_host: str = Field("localhost", alias="DB_HOST")
    db_port: int = Field(5432, alias="DB_PORT")
    db_name: str = Field("shop", alias="DB_NAME")
    db_user: str = Field("postgres", alias="DB_USER")
    db_pass: str = Field("postgres", alias="DB_PASS")

    database_url: str = Field(..., alias="DATABASE_URL")

    product_service_url: str = Field(..., alias="PRODUCT_SERVICE_URL")
    secret_key: str = Field("super_secret_key", alias="JWT_SECRET")
    algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire: int = Field(120, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    cors_origins: str = Field("", alias="CORS_ORIGINS")

    static_dir: str = Field("static", alias="STATIC_DIR")
    images_dir: str = Field("static/images", alias="IMAGES_DIR")

    @property
    def async_database_url(self) -> str:
        return self.database_url
    
    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
