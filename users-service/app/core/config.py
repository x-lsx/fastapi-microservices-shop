from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List, Union
import os 

class Settings(BaseSettings):
    app_name: str = "FastAPI Shop"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./shop.db"  

    cors_origins: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        
    ]

    SECRET_KEY: str = Field("super_secret_key_change_me", alias="JWT_SECRET")
    ALGORITHM: str = Field("HS256", alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(120, alias="ACCESS_TOKEN_EXPIRE_MINUTES") 

    static_dir: str = "static"
    images_dir: str = "static/images"
    
    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"


settings = Settings()
