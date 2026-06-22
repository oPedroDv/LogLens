from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.storage.queries import (
    get_log_file_by_id,
    save_analysis,
    get_analyses_for_file,
)
from app.analysis.parser import parse_file_content
from app.analysis.statistics import build_analysis_result
from app.analysis.insights import generate_insights
from app.analysis.clustering import cluster_entries, summarize_clusters
from app.schemas.response import AnalysisResponse, ClusterResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/{file_id}", response_model=AnalysisResponse, status_code=201)
def analyze_log_file(
    file_id: str,
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    log_file = get_log_file_by_id(db, file_id)
    if log_file is None:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    stored_path = Path(log_file.stored_path)
    if not stored_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Arquivo registrado no banco não foi encontrado em disco.",
        )
    content = stored_path.read_bytes()

    entries = parse_file_content(content, file_id=log_file.id)

    result = build_analysis_result(
        entries=entries,
        file_id=log_file.id,
        file_name=log_file.original_name,
    )

    result.insights = generate_insights(result)

    clusters = cluster_entries(entries, only_errors=True, min_cluster_size=2)
    cluster_summaries = summarize_clusters(clusters, limit=10)

    record = save_analysis(
        db=db,
        log_file_id=log_file.id,
        total_lines=result.total_lines,
        parsed_lines=result.parsed_lines,
        error_rate=result.level_distribution.error_rate,
        has_errors=result.has_errors,
        result_data=result.summary(), 
    )

    return AnalysisResponse(
        analysis_id=record.id,
        file_id=log_file.id,
        file_name=log_file.original_name,
        analyzed_at=record.analyzed_at,
        total_lines=result.total_lines,
        parsed_lines=result.parsed_lines,
        parse_rate=f"{result.parse_success_rate:.1%}",
        has_errors=result.has_errors,
        error_rate=f"{result.level_distribution.error_rate:.1%}",
        time_range={
            "start": result.time_range.start.isoformat(),
            "end": result.time_range.end.isoformat(),
            "duration": result.time_range.duration_human,
        } if result.time_range else None,
        top_sources=result.top_sources,
        insights=result.insights,
        clusters=[ClusterResponse(**c) for c in cluster_summaries],
    )


@router.get("/{file_id}/history")
def get_analysis_history(file_id: str, db: Session = Depends(get_db)):
    log_file = get_log_file_by_id(db, file_id)
    if log_file is None:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    analyses = get_analyses_for_file(db, file_id)
    return [
        {
            "analysis_id": a.id,
            "analyzed_at": a.analyzed_at,
            "summary": a.result_data,
        }
        for a in analyses
    ]