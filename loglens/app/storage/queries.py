from sqlalchemy.orm import Session
from sqlalchemy import select

from app.storage.models import LogFile, AnalysisRecord

def save_log_file(
    db: Session,
    original_name: str,
    stored_path: str,
    size_bytes: int,
    content_hash: str,
) -> LogFile:
    log_file = LogFile(
        original_name=original_name,
        stored_path=stored_path,
        size_bytes=size_bytes,
        content_hash=content_hash,
    )
    db.add(log_file)
    db.commit()
    db.refresh(log_file)
    return log_file


def get_log_file_by_id(db: Session, file_id: str) -> LogFile | None:
    return db.get(LogFile, file_id)

def get_log_file_by_hash(db: Session, content_hash: str) -> LogFile | None:
    stmt = select(LogFile).where(LogFile.content_hash == content_hash)
    return db.execute(stmt).scalar_one_or_none()

def list_log_files(db: Session, limit: int = 50, offset: int = 0) -> list[LogFile]:
    stmt = (
        select(LogFile)
        .order_by(LogFile.uploaded_at.desc())  # mais recentes primeiro
        .limit(limit)
        .offset(offset)
    )
    return list(db.execute(stmt).scalars().all())


def delete_log_file(db: Session, log_file: LogFile) -> None:
    db.delete(log_file)
    db.commit()

def save_analysis(
    db: Session,
    log_file_id: str,
    total_lines: int,
    parsed_lines: int,
    error_rate: float,
    has_errors: bool,
    result_data: dict,
) -> AnalysisRecord:
    record = AnalysisRecord(
        log_file_id=log_file_id,
        total_lines=total_lines,
        parsed_lines=parsed_lines,
        error_rate=error_rate,
        has_errors=has_errors,
        result_data=result_data,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_analysis_by_id(db: Session, analysis_id: str) -> AnalysisRecord | None:
    return db.get(AnalysisRecord, analysis_id)


def get_analyses_for_file(db: Session, log_file_id: str) -> list[AnalysisRecord]:
    stmt = (
        select(AnalysisRecord)
        .where(AnalysisRecord.log_file_id == log_file_id)
        .order_by(AnalysisRecord.analyzed_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def list_analyses_with_errors(db: Session, limit: int = 50) -> list[AnalysisRecord]:
    stmt = (
        select(AnalysisRecord)
        .where(AnalysisRecord.has_errors == True)  # noqa: E712
        .order_by(AnalysisRecord.analyzed_at.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())