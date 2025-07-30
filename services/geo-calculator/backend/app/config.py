import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "RankMyBrand GEO Calculator"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://rankmybrand.ai"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./geo_metrics.db"
    
    # AI Platforms
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Rate Limiting
    RATE_LIMIT_PER_HOUR: int = 100
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"

settings = Settings()
