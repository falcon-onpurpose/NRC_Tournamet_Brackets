"""
Configuration settings for NRC Tournament Program
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    # Application Settings
    APP_NAME: str = "NRC Tournament Program"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./nrc_tournament.db"
    DATABASE_PASSWORD: Optional[str] = None
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Arena Integration Settings
    ARENA_API_URL: str = "http://localhost:8001"
    ARENA_API_KEY: str = "arena-api-key"
    ARENA_TIMEOUT: int = 30
    
    # Tournament Settings
    DEFAULT_MATCH_DURATION: int = 120  # seconds
    DEFAULT_PIT_ACTIVATION_TIME: int = 60  # seconds
    MAX_TEAMS_PER_TOURNAMENT: int = 64
    MAX_SWISS_ROUNDS: int = 10
    
    # Multi-User Settings
    MAX_CONCURRENT_USERS: int = 10
    SESSION_TIMEOUT_MINUTES: int = 60
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_CSV_EXTENSIONS: List[str] = [".csv"]
    UPLOAD_DIR: str = "./uploads"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Cross-Platform Settings
    PLATFORM: str = "unknown"
    IS_RASPBERRY_PI: bool = False
    
    # Performance Settings
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_RECYCLE: int = 300
    
    # Public Display Settings
    PUBLIC_DISPLAY_REFRESH_RATE: int = 5  # seconds
    PUBLIC_DISPLAY_TIMEOUT: int = 300  # seconds
    
    # Export Settings
    EXPORT_DIR: str = "./exports"
    MAX_EXPORT_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Archive Settings
    ARCHIVE_DIR: str = "./archives"
    MAX_ARCHIVE_SIZE: int = 500 * 1024 * 1024  # 500MB
    


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._detect_platform()
        self._create_directories()
        self._validate_settings()

    def _detect_platform(self):
        """Detect the current platform and set appropriate defaults"""
        import platform
        import subprocess
        
        system = platform.system().lower()
        
        if system == "linux":
            # Check if running on Raspberry Pi
            try:
                with open("/proc/cpuinfo", "r") as f:
                    if "Raspberry Pi" in f.read():
                        self.PLATFORM = "raspberry_pi"
                        self.IS_RASPBERRY_PI = True
                        self._set_raspberry_pi_defaults()
                    else:
                        self.PLATFORM = "linux"
            except:
                self.PLATFORM = "linux"
        elif system == "darwin":
            self.PLATFORM = "macos"
        elif system == "windows":
            self.PLATFORM = "windows"
        else:
            self.PLATFORM = "unknown"

    def _set_raspberry_pi_defaults(self):
        """Set Raspberry Pi specific defaults"""
        self.DATABASE_POOL_SIZE = 5
        self.DATABASE_MAX_OVERFLOW = 10
        self.MAX_CONCURRENT_USERS = 5
        self.DEBUG = False
        
        # Use SQLite by default on Pi for simplicity
        if self.DATABASE_URL.startswith("postgresql"):
            self.DATABASE_URL = "sqlite:///./nrc_tournament.db"

    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.UPLOAD_DIR,
            self.EXPORT_DIR,
            self.ARCHIVE_DIR
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def _validate_settings(self):
        """Validate configuration settings"""
        if self.DATABASE_URL.startswith("sqlite"):
            # Ensure SQLite database directory exists
            db_path = Path(self.DATABASE_URL.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Validate file paths
        if not os.path.exists(self.UPLOAD_DIR):
            raise ValueError(f"Upload directory does not exist: {self.UPLOAD_DIR}")
        
        if not os.path.exists(self.EXPORT_DIR):
            raise ValueError(f"Export directory does not exist: {self.EXPORT_DIR}")
        
        if not os.path.exists(self.ARCHIVE_DIR):
            raise ValueError(f"Archive directory does not exist: {self.ARCHIVE_DIR}")

    @property
    def database_config(self):
        """Get database configuration based on platform"""
        if self.DATABASE_URL.startswith("sqlite"):
            return {
                "url": self.DATABASE_URL,
                "connect_args": {"check_same_thread": False},
                "echo": self.DEBUG
            }
        else:
            return {
                "url": self.DATABASE_URL,
                "pool_size": self.DATABASE_POOL_SIZE,
                "max_overflow": self.DATABASE_MAX_OVERFLOW,
                "pool_recycle": self.DATABASE_POOL_RECYCLE,
                "echo": self.DEBUG,
                "pool_pre_ping": True
            }

    @property
    def server_config(self):
        """Get server configuration"""
        return {
            "host": self.HOST,
            "port": self.PORT,
            "reload": self.RELOAD,
            "log_level": self.LOG_LEVEL.lower()
        }

    @property
    def arena_config(self):
        """Get arena integration configuration"""
        return {
            "api_url": self.ARENA_API_URL,
            "api_key": self.ARENA_API_KEY,
            "timeout": self.ARENA_TIMEOUT
        }

    def get_environment_info(self):
        """Get environment information for diagnostics"""
        import platform
        import sys
        
        return {
            "platform": self.PLATFORM,
            "is_raspberry_pi": self.IS_RASPBERRY_PI,
            "python_version": sys.version,
            "system": platform.system(),
            "architecture": platform.machine(),
            "database_url": self.DATABASE_URL.replace(self.DATABASE_PASSWORD or "", "***") if self.DATABASE_PASSWORD else self.DATABASE_URL,
            "debug": self.DEBUG,
            "max_concurrent_users": self.MAX_CONCURRENT_USERS,
            "arena_api_url": self.ARENA_API_URL
        }

_settings_singleton: Optional[Settings] = None

def get_settings() -> Settings:
    global _settings_singleton
    if _settings_singleton is None:
        _settings_singleton = Settings()
    return _settings_singleton

# Environment-specific overrides
settings = get_settings()

if settings.DEBUG:
    settings.RELOAD = True
    settings.LOG_LEVEL = "DEBUG"

if settings.PLATFORM == "raspberry_pi":
    # Raspberry Pi specific optimizations
    settings.DATABASE_POOL_SIZE = 5
    settings.DATABASE_MAX_OVERFLOW = 10
    settings.MAX_CONCURRENT_USERS = 5
    settings.PUBLIC_DISPLAY_REFRESH_RATE = 10  # Slower refresh on Pi

# Production overrides
if os.getenv("ENVIRONMENT") == "production":
    settings.DEBUG = False
    settings.RELOAD = False
    settings.LOG_LEVEL = "WARNING"
    settings.SECRET_KEY = os.getenv("SECRET_KEY", settings.SECRET_KEY)
    
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
        raise ValueError("SECRET_KEY must be set in production environment")
