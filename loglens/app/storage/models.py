import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class LogFile(Base):
    __tablename__ = "log_files"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    original_name: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    size_bytes: Mapped[int] = mapped_column(Integer)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    analyses: Mapped[list["AnalysisRecord"]] = relationship(
        back_populates="log_file",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<LogFile {self.original_name} ({self.size_bytes} bytes)>"
    
class AnalysisRecord(Base):
    __tablename__ = "analysis_records"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )

    log_file_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("log_files.id")
    )

    log_file: Mapped["LogFile"] = relationship(back_populates="analyses")
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    total_lines: Mapped[int] = mapped_column(Integer)
    parsed_lines: Mapped[int] = mapped_column(Integer)
    error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    has_errors: Mapped[bool] = mapped_column(Boolean, default=False)
    result_data: Mapped[dict] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<AnalysisRecord {self.id} errors={self.error_rate:.1%}>"