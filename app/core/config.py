from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive = True)

    PROJECT_NAME: str = "FRONTNIX"
    PROJECT_VERSION: str = "1.0.0"

    DATABASE_URL: str
    
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-this-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Cloud Pub/Sub Configuration
    GCP_PROJECT_ID: str = "serjava-demo"
    PUBSUB_TOPIC: str = "pi-smarttruck-pub"
    PUBSUB_SUBSCRIPTION: str = "pi-smarttruck-sub"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None  # Path to service account JSON
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:8081,http://localhost:3000,http://localhost:3030,https://frotinix.eastus2.cloudapp.azure.com,https://frotinix.vercel.app"


settings = Settings()
