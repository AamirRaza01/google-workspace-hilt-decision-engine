"""
Settings and Configuration Management
Handles all environment variables type-validation securely via Pydantic.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    """
    Application configurations. Values are parsed directly from 
    the system environment or a local .env file.
    """
    
    # Google Gemini GenAI SDK
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash" 
    
    # Google Workspace Credential Configurations
    google_credentials_path: str = "credentials.json"
    google_token_path: str = "token.json"
    google_scopes: list[str] = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/tasks'
    ]
    
    # Vector Database Settings
    chroma_persist_directory: str = "./data/chroma_db"
    chroma_collection_name: str = "workspace_agent_xai_memory"
    
    # Execution Memory Configuration
    max_conversation_history: int = 30
    summarization_threshold: int = 15
    
    # Logging Telemetry
    log_level: str = "INFO"
    log_file: str = "./logs/workspace_agent.log"
    
    # Agent Constraints
    max_iterations: int = 10
    
    # Tell Pydantic how to handle environment resolution
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def ensure_directories(self):
        """Ensure local storage directories exist safely at runtime."""
        Path(self.chroma_persist_directory).mkdir(parents=True, exist_ok=True)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        Path("data").mkdir(exist_ok=True)

@lru_cache()
def get_settings() -> Settings:
    """Provides a globally cached singleton instance of configuration settings."""
    settings = Settings()
    settings.ensure_directories()
    return settings