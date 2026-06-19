from collections import Counter
from datetime import datetime

from app.types.log_entry import LogEntry
from app.types.analysis_result import AnalysisResult, TimeRange, LevelDistribution

def compute_level_distribution(entries: list[LogEntry]) -> LevelDistribution:
    distribution = LevelDistribution()
    for entry in entries:
        distribution.add(entry.level)
    return distribution

def compute_time_range(entries: list[LogEntry]) -> TimeRange | None:
    timestamps = [e.timestamp for e in entries if e.timestamps is not None]

    if not timestamp:
        return None
    return TimeRange(start=min(timestamps), end=max(timestamps))

def compute_top_sources(entries: list[LogEntry], limit: int=10) -> list[tuple[str, int]]:
    sources = [e.source for e in entries if e.source is not None]
    counter = Counter(sources)
    return counter.most_common(limit)

def compute_error_sources(entries: list[LogEntry], limit: int=10) -> list[tuple[str, int]]:
    error_sources = [e.source for e in entries if e.source is not None and e.is_error()]
    return counter.most_common(limit)

def compute_hourly_distribution(entris: list[LogEntry]) -> dict[int, int]:
    hour_counts: Counter[int] = Counter()
    for entry in entries:
        if entry.timestamp:
            hour_counts[entry.timestamp.hour] += 1
    
    return {hour: hour_counts.get(hour, 0) for hour in range(24)}

def build_analysis_result(
        entries: list[LogEntry],
        file_id: str,
        file_name: str,
) -> AnalysisResult:
    
    parsed_count = sum(1 for e in entries if e.parsed)
    failed_count = len(entries) - parsed_count

    result = AnalysisResult(
        file_id=file_id,
        file_name=file_name,
        entries=entries,
        total_lines=len(entries),
        parsed_lines=parsed_count,
        failed_lines=failed_count,
        level_distribution=compute_level_distribution(entries),
        time_range=compute_time_range(entries),
        top_sources=compute_top_sources(entries),
    )
    
    return result