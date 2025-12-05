"""Configuration module for Department Configurator."""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application credentials
    APP_URL: str
    APP_USERNAME: str
    APP_PASSWORD: str
    
    # Browser settings
    HEADLESS: bool = False
    WINDOW_SIZE: str = "1920,1080"
    CHROME_BINARY: Optional[str] = None
    BLOCK_IMAGES: int = 2
    
    # Timeouts
    DEFAULT_TIMEOUT: int = 10
    LONG_TIMEOUT: int = 30
    
    # Configuration
    DOCUMENT_NAME: str = "Contábil - teste"
    DEPARTMENT_SEARCH: str = "Contábil"
    
    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent
    LOGS_DIR: Path = BASE_DIR / "logs"
    SCREENSHOTS_DIR: Path = BASE_DIR / "screenshots"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
