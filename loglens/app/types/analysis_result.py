from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from collections import Counter

from app.types.log_entry import LogEntry, LogLevel


@dataclass
class TimeRange:
    start: datetime
    end:   datetime

    @property
    def duration_seconds(self) -> float:
        return (self.end - self.start).total_seconds()

    @property
    def duration_human(self) -> str:
        """Retorna algo legível como '2h 15m 30s'."""
        total = int(self.duration_seconds)
        h, remainder = divmod(total, 3600)
        m, s = divmod(remainder, 60)
        parts = []
        if h: parts.append(f"{h}h")
        if m: parts.append(f"{m}m")
        if s or not parts: parts.append(f"{s}s")
        return " ".join(parts)


@dataclass
class LevelDistribution:
    _counts: Counter = field(default_factory=Counter)

    def add(self, level: LogLevel) -> None:
        self._counts[level] += 1

    @property
    def total(self) -> int:
        return sum(self._counts.values())

    @property
    def error_rate(self) -> float:
        if self.total == 0:
            return 0.0
        errors = self._counts[LogLevel.ERROR] + self._counts[LogLevel.CRITICAL]
        return errors / self.total

    def to_dict(self) -> dict[str, int]:
        return {level.value: self._counts[level] for level in LogLevel}


@dataclass
class AnalysisResult:
    file_id:   str       # ID único do arquivo
    file_name: str       # nome original do arquivo
    analyzed_at: datetime = field(default_factory=datetime.utcnow)

    entries:       list[LogEntry] = field(default_factory=list)
    total_lines:   int = 0
    parsed_lines:  int = 0
    failed_lines:  int = 0

    level_distribution: LevelDistribution = field(
        default_factory=LevelDistribution
    )
    time_range: Optional[TimeRange] = None   # None se nenhum timestamp foi achado
    top_sources: list[tuple[str, int]] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)

    @property
    def parse_success_rate(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return self.parsed_lines / self.total_lines

    @property
    def has_errors(self) -> bool:
        return self.level_distribution.error_rate > 0

    def summary(self) -> dict:
        return {
            "file_id":        self.file_id,
            "file_name":      self.file_name,
            "analyzed_at":    self.analyzed_at.isoformat(),
            "total_lines":    self.total_lines,
            "parsed_lines":   self.parsed_lines,
            "parse_rate":     f"{self.parse_success_rate:.1%}",
            "has_errors":     self.has_errors,
            "error_rate":     f"{self.level_distribution.error_rate:.1%}",
            "time_range":     {
                "start":    self.time_range.start.isoformat(),
                "end":      self.time_range.end.isoformat(),
                "duration": self.time_range.duration_human,
            } if self.time_range else None,
            "top_sources":    self.top_sources[:5],
            "insights":       self.insights,
        }