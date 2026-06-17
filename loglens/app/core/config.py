from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "LogLens"
    app_version: str = "0.1.0"
    debug: bool = False
    base_dir: Path = Path(__file__).resolve().parent.parent.parent

    @property
    def upload_dir(self) -> Path:
        return self.base_dir / "data" / "reports"
    
    database_url: str = "sqlite:///./data/loglens.db"

    max_file_size_mb: int = 50
    allowed_exstensions = tuple[str, ...] = (".log", ".txt")

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024
    
    chunk_size: int = 5000

    model_config = SettingsConfigDict(
        env_files = ".env",
        env_prefix = "LOGLENS_",
        extra = "ignore",
    )

@lru_cache
def get_settigns() -> Settings:
    return Settings()
