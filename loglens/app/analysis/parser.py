# app/analysis/parser.py
import re
from datetime import datetime
from typing import Optional

from app.types.log_entry import LogEntry, LogLevel

TIMESTAMP_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?"), "%Y-%m-%dT%H:%M:%S.%f"),
    (re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"), "%Y-%m-%dT%H:%M:%S"),
    (re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+"), "%Y-%m-%d %H:%M:%S,%f"),
    (re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"), "%Y-%m-%d %H:%M:%S"),
    (re.compile(r"[A-Z][a-z]{2}\s+\d{1,2} \d{2}:\d{2}:\d{2}"), "%b %d %H:%M:%S"),
]

LEVEL_KEYWORDS: list[tuple[str, LogLevel]] = [
    ("CRITICAL", LogLevel.CRITICAL),
    ("FATAL", LogLevel.CRITICAL),
    ("ERROR", LogLevel.ERROR),
    ("ERR", LogLevel.ERROR),
    ("WARNING", LogLevel.WARNING),
    ("WARN", LogLevel.WARNING),
    ("INFO", LogLevel.INFO),
    ("DEBUG", LogLevel.DEBUG),
    ("TRACE", LogLevel.DEBUG),
]

SOURCE_PATTERN = re.compile(r"\[([^\]]{1,50})\]")

def _extract_timestamp(line: str) -> Optional[datetime]:
    for pattern, fmt in TIMESTAMP_PATTERNS:
        match = pattern.search(line)
        if match:
            try:
                raw = match.group(0).rstrip("Z")
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
    return None


def _extract_level(line: str) -> LogLevel:
    upper = line.upper()
    for keyword, level in LEVEL_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper):
            return level
    return LogLevel.UNKNOWN


def _extract_source(line: str) -> Optional[str]:
    for match in SOURCE_PATTERN.finditer(line):
        candidate = match.group(1)
        if not re.search(r"\d{4}-\d{2}-\d{2}", candidate):
            return candidate.strip()
    return None


def _extract_message(line: str, timestamp: Optional[datetime], level: LogLevel, source: Optional[str]) -> str:
    message = line

    if timestamp:
        for pattern, _ in TIMESTAMP_PATTERNS:
            message = pattern.sub("", message, count=1)
            if message != line:
                break

    if level != LogLevel.UNKNOWN:
        message = re.sub(
            rf"\b{level.value}\b",
            "",
            message,
            flags=re.IGNORECASE,
            count=1,
        )
        synonyms = {"CRITICAL": "FATAL", "ERROR": "ERR", "WARNING": "WARN", "DEBUG": "TRACE"}
        if level.value in synonyms:
            message = re.sub(rf"\b{synonyms[level.value]}\b", "", message, flags=re.IGNORECASE, count=1)

    if source:
        message = message.replace(f"[{source}]", "", 1)

    message = re.sub(r"[\[\]:]+", " ", message)
    message = re.sub(r"\s{2,}", " ", message)
    return message.strip()

def parse_line(line: str, line_number: int) -> LogEntry:
    stripped = line.strip()

    if not stripped:
        return LogEntry(
            raw_line=line,
            line_number=line_number,
            parsed=False,
        )

    timestamp = _extract_timestamp(stripped)
    level     = _extract_level(stripped)
    source    = _extract_source(stripped)
    message   = _extract_message(stripped, timestamp, level, source)
    successfully_parsed = timestamp is not None or level != LogLevel.UNKNOWN

    return LogEntry(
        raw_line=line,
        line_number=line_number,
        timestamp=timestamp,
        level=level,
        source=source,
        message=message if message else stripped,
        parsed=successfully_parsed,
    )


def parse_file_content(content: bytes, file_id: str) -> list[LogEntry]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    lines = text.splitlines()
    entries: list[LogEntry] = []

    for line_number, line in enumerate(lines, start=1):
        entry = parse_line(line, line_number)
        entry.file_id = file_id
        entries.append(entry)

    return entries