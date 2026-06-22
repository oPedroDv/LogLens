from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LogFileResponse(BaseModel):
    id: str
    original_name: str
    stored_path: str
    size_bytes: int
    content_hash: str
    uploaded_at: datetime
    is_duplicate: bool = False

    model_config = ConfigDict(from_attributes=True)


class ClusterResponse(BaseModel):
    signature: str
    count: int
    level: str
    example: str
    first_line: int
    last_line: int


class AnalysisResponse(BaseModel):
    analysis_id: str
    file_id: str
    file_name: str
    analyzed_at: datetime

    total_lines: int
    parsed_lines: int
    parse_rate: str
    has_errors: bool
    error_rate: str

    time_range: dict | None
    top_sources: list[tuple[str, int]]
    insights: list[str]
    clusters: list[ClusterResponse]

    model_config = ConfigDict(from_attributes=True)