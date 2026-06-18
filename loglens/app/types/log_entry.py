from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

@dataclass
class LogEntry:

    raw_line: str                       # linha original
    line_number: int                    # posição do arquivo
    timestamp: Optional[datetime] = None
    level: LogLevel = LogLevel.UNKNOWN
    source: Optional[str] = None
    message: Optional[str]= None
    parsed: bool = False
    file_id: Optional[str] = None

    def is_error(self) -> bool:
        return self.level in (LogLevel.ERROR, LogLevel.CRITICAL)            # atalho pra filtrar problema

    def __repr__(self) -> str:
        ts = self.timestamp.isoformat() if self.timestamp else "no-timestamp"
        return f"<LogEntry #{self.line_number} [{self.level}] {ts}>"
