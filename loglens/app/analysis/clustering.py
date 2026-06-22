import re
from dataclasses import dataclass, field
from collections import defaultdict

from app.types.log_entry import LogEntry, LogLevel

NORMALIZED_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE), "<UUID>"),
    (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "<IP>"),
    (re.compile(r"(?:/[\w\-.]+){2,}"), "<PATH>"),
    (re.compile(r"\b[0-9a-f]{8,}\b", re.IGNORECASE), "<HASH>"),
    (re.compile(r"\b\d+\b"), "<N>"),
    (re.compile(r'"[^"]*"'), "<STR>"),
    (re.compile(r"'[^']*'"), "<STR>"),
]

def normalize_message(message: str) -> str:
    normalized =  message
    for pattern, placeholder in NORMALIZED_PATTERNS:
        normalized = pattern.sub(placeholder, normalized)

    normalized =  re.sub(r"\s{2,}", " ", normalized)
    return normalized.strip()

@dataclass
class LogCluster:
    signature: str
    entries: list[LogEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)
    
    @property
    def example_message(self) -> str:
        return self.entries[0].message if self.entries else ""
    
    @property
    def dominant_level(self) -> LogLevel:
        if not self.entries:
            return LogLevel.UNKNOWN
        level_counts = defaultdict(int)
        for entry in self.entries:
            level_counts[entry.level] += 1
        return max(level_counts, key=level_counts.get)
    
    def to_dict(self) -> dict:
        return {
            "signature": self.signature,
            "count": self.count,
            "level": self.dominant_level.value,
            "example": self.example_message,
            "first_line": min(e.line_number for e in self.entries),
            "last_line": max(e.line_number for e in self.entries),
        }
    
def cluster_entries(
        entries: list[LogEntry],
        only_errors: bool = True,
        min_cluster_size: int = 2,
) -> list[LogCluster]:
    
    candidates = entries
    if only_errors:
        candidates = [e for e in entries if e.is_error()]

    groups: dict[str, list[LogEntry]] = defaultdict(list)

    for entry in candidates:
        if not entry.message:
            continue
        signature = normalize_message(entry.message)
        groups[signature].append(entry)

    clusters = [
        LogCluster(signature = signature, entries=group_entries)
        for signature, group_entries in groups.items()
        if len(group_entries) >= min_cluster_size
    ]

    clusters.sort(key=lambda c: c.count, reverse=True)
    return clusters

def summarize_clusters(clusters: list[LogCluster], limit: int = 10) -> list[dict]:
    return [cluster.to_dict() for cluster in clusters[:limit]]